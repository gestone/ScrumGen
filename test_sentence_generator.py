from sentence_generator import SentenceGenerator
import json
import unittest

class TestSentenceGenerator(unittest.TestCase):
    """
    Tests external functionality of the SentenceGenerator class.
    """

    def setUp(self):
        self.gen = SentenceGenerator()

    def test_train_model_single_words(self):
        """
        Test single word mappings so that each word
        has only one possible word that proceeds it.
        """
        self.gen.train_model("The brown fox.")
        self.assertEquals(self.gen.model, {"The" : ["brown"], "brown" : ["fox."]})

    def test_train_model_multi_words(self):
        """
        Test multi word mappings such that each word
        has two possible words that proceed it.
        """
        self.gen.train_model("The brown brown fox.")
        self.assertEquals(self.gen.model, {"The" : ["brown"], "brown" : ["brown", "fox."]})

    def test_train_model_no_end_word(self):
        """
        Test if the model has no end punctuation, ".", "?", "!", or ":"
        that it successfully appends a "." to the end.
        """
        self.gen.train_model("The brown fox")
        self.assertEquals(self.gen.model, {"The" : ["brown"], "brown" : ["fox."]})

    def test_train_model_empty_input(self):
        """
        Test that the empty input does not modify the model.
        """
        self.gen.train_model("")
        self.assertEquals(self.gen.model, {})

    def test_generate_sentence_invalid_key(self):
        """
        Test that a ValueError is thrown if the key
        is not present in the model.
        """
        self.gen.train_model("The brown fox.")
        self.assertRaises(ValueError, lambda: self.gen.generate_sentences(1, "wolf"))

    def test_generate_sentence_initial_word(self):
        """
        Test that the initial word is being applied if
        the it is valid and is specified.
        """
        self.gen.train_model("The brown fox jumped over the lazy fat dog and the big log.")

        generated_sentences = self.gen.generate_sentences(100, "The")

        # Generate many sentences so that the test does not succeed by chance.
        for sentence in generated_sentences:
            self.assertEquals(sentence.split(" ", 1)[0], "The")

    def test_length_generated_sentences(self):
        """
        Test that the number of generated sentences
        specified is the number of sentences returned.
        """
        self.gen.train_model("The brown fox jumped over the lazy fat dog and the big log.")
        self.assertEquals(len(self.gen.generate_sentences(100)), 100)

    def test_json_representation(self):
        """
        Test that the correct json representation is being
        returned from the model.
        """
        self.gen.train_model("The brown fox.")
        expected_structure = {"The" : ["brown"], "brown" : ["fox."]}
        self.assertEquals(self.gen.get_json_rep(), json.dumps(expected_structure))

if __name__ == "__main__":
    unittest.main()
