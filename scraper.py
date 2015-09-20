"""
Scrapes both Reddit and HN for new comments
to insert into the database.
"""
import praw  # reddit api
import multiprocessing as mp  # speed up collecting data
import urllib2  # for making requests to the HackerNews API
import re
import psycopg2

from bs4 import BeautifulSoup # for parsing HackerNews
from hackernews import HackerNews # for getting all the HackerNews posting ids

DEFAULT_SUBREDDITS = ["programming", "python", "coding", "java", "webdev", "machinelearning", \
                      "node", "linux"]

NUM_SUBREDDITS_PROCESSOR = 1  # the number of subreddits each process will process
NUM_HN_THREAD_PROCESSOR = 2 # the number of HN threads each process will process
HN_BASE_API_ENDPOINT = "https://news.ycombinator.com/item?id="

class Scraper(object):
    """
    Scrapes various services, namely Reddit and HackerNews
    used to gather data to feed into the SentenceGenerator
    model.
    """

    def __init__(self, logger):
        """
        Initializes an instance of Scraper. Requires that a logger
        to denote the progress of the Scraper to be passed in.
        """
        self.phrases = []
        self.hackernews = HackerNews()
        self.output = mp.Queue()
        self.logger = logger


    def gather_reddit_data(self):
        """
        Gathers comments and submission titles from Reddit.
        Returns an updated list of pharses after the Reddit data has been gathered.
        """

        # split the list of subreddits to allow for parallel processing
        subreddit_sublists = Scraper._split_into_sublists(DEFAULT_SUBREDDITS, \
                                NUM_SUBREDDITS_PROCESSOR)

        # setup processes, run, and collect results
        reddit_processes = [mp.Process(target=self._gather_reddit_data, args=(subreddits,)) \
                            for subreddits in subreddit_sublists]

        self._execute_and_collect_processes(reddit_processes)

    def gather_hn_data(self):
        """
        Gathers comments and submission titles from HN.
        Returns an updated list of pharses after the HN data has been gathered.
        """

        # get top stories from HN and split the list
        top_stories = self.hackernews.top_stories()[:3]
        stories_sublists = Scraper._split_into_sublists(top_stories, NUM_HN_THREAD_PROCESSOR)
        hn_processes = [mp.Process(target=self._gather_hn_data, args=(stories,))
                        for stories in stories_sublists]

        self._execute_and_collect_processes(hn_processes)

    def _execute_and_collect_processes(self, processes):
        """
        Executes and collects the results of the phrases the scraper has gathered.
        """

        for p_num, process in enumerate(processes):
            self.logger.debug("Starting process %d " % p_num)
            process.start()

        for p_num, process in enumerate(processes):
            self.logger.debug("Joining process %d " % p_num)
            process.join()

        self.logger.debug("Combining results")
        while self.output.qsize():
            phrase = self.output.get()
            self.phrases.append(phrase)

    @classmethod
    def _split_into_sublists(cls, lst, size):
        """
        Splits the list, lst, into sublists of size 'size'.
        Returns a new list consisting of len(l) / size sublists
        of size 'size'.
        """
        sublists = []
        for i in xrange(0, len(lst), size):
            sublists.append(lst[i : i + size])
        return sublists


    def _gather_reddit_data(self, subreddits):
        """
        Gathers data from the Reddit API. The param, subreddits,
        are all the subreddits this process will gather data from
        and output represents the joint result of multiple threads.
        """

        reddit = praw.Reddit(user_agent="Scrum Generator")
        for subreddit in subreddits:
            # force lazy eval by converting to list
            top_submissions = list(reddit.get_subreddit(subreddit).get_top(limit=2))
            titles = [entry.title.encode("utf8", "ignore") for entry in top_submissions]
            comments = sum([[c.body for c in submission.comments \
                            if not isinstance(c, praw.objects.MoreComments)] \
                            for submission in top_submissions], [])

            for comment in comments:
                self.output.put(Scraper._clean_data(comment))

            for title in titles:
                self.output.put(Scraper._clean_data(title))

    def _gather_hn_data(self, entries):
        """
        Gathers data from the Hacker News API. The param, entries,
        represents all of the posts this process will gather data
        from.
        """
        for entry in entries:
            response = urllib2.urlopen(HN_BASE_API_ENDPOINT + str(entry)).read()
            soup = BeautifulSoup(response, "html.parser")
            all_comments = soup.findAll("span", {"class" : "comment"})
            for comment in all_comments:
                cleaned_html = re.sub('<[^<]+?>|reply|\n', "", comment.text)
                cleaned_data = Scraper._clean_data(cleaned_html)
                self.output.put(cleaned_data)


    @classmethod
    def _clean_data(cls, phrase):
        """
        Cleans each phrase from both Reddit and HackerNews
        to be processed by SentenceGenerator.
        Returns a cleaned string free of parens, curly and square
        brackets, and quotes along with spaces after punctuation.
        """

        # replace illegal chracaters
        cleaned_phrase = re.sub("[(%~`<>#:@/^*&$\t?=|){}\\[\\]\"\n]", "", phrase)
        # make sure each period is proceeded by a space for proper punctuation
        cleaned_phrase = re.sub(r'[?!.]([a-zA-Z])', r'. \1', cleaned_phrase)

        return cleaned_phrase

    def insert_into_db(self):
        """
        Inserts the data into the Postgres DB.
        """
        self.logger.debug("Inserting data into database")
        conn = psycopg2.connect(database="textclassify", user="justinharjanto")
        cur = conn.cursor()

        sql_string = "INSERT INTO phrases (phrase, link_id, record_date) \
                      VALUES (%s, to_timestamp(%s), %s) "
        cur.execute(sql_string)
