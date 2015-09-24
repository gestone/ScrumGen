(function() {

    "use strict";

    var HEIGHT_SCALE = 5;
    var WINDOW_CUTOFF = 1000; // to rescale properly for mobile devices

    /**
    * Sets the initial state of the page. Hides the response
    * container, sets the onclick listener to generate a sentence,
    * and scales the video container to an appropriate size so that
    * the video can be rendered properly.
    */
    $(document).ready(function() {
        $("#response-container").hide();
        $("#gen-sentence").click(getSentence);

        scaleVideoContainer();

        initBannerVideoSize('.video-container .poster img');
        initBannerVideoSize('.video-container .filter');
        initBannerVideoSize('.video-container video');

        $(window).on('resize', function() {
            scaleVideoContainer();
            scaleBannerVideoSize('.video-container .poster img');
            scaleBannerVideoSize('.video-container video');
        });
    });

    /**
    * Scales the video container properly to fit the .mp4 video in.
    */
    function scaleVideoContainer() {
        var height = $(window).height() + HEIGHT_SCALE;
        var unitHeight = parseInt(height, 10) + 'px';
        $('.homepage-hero-module').css('height', unitHeight);
    }

    /**
    * Initializes the size of the banner on page load.
    */
    function initBannerVideoSize(element){
        $(element).each(function(){
            $(this).data('height', $(this).height());
            $(this).data('width', $(this).width());
        });
        scaleBannerVideoSize(element);
    }

    /**
    * Resizes the video to fit the new screen size.
    * @param element The element on the page to be resized.
    */
    function scaleBannerVideoSize(element){
        var windowWidth = $(window).width(),
        windowHeight = $(window).height() + HEIGHT_SCALE,
        videoWidth,
        videoHeight;
        $(element).each(function() {
            var videoAspectRatio = $(this).data('height') / $(this).data('width');
            $(this).width(windowWidth);
            if (windowWidth < WINDOW_CUTOFF) {
                videoHeight = windowHeight;
                videoWidth = videoHeight / videoAspectRatio;
                $(this).css({'margin-top' : 0, 'margin-left' : -(videoWidth - windowWidth) / 2 + 'px'});
                $(this).width(videoWidth).height(videoHeight);
            }
            $('.homepage-hero-module .video-container video').addClass('fadeIn animated');
        });
    }

    /**
    * Sends a GET request to the server to get a sentence to be displayed 
    * to the user. On a successful response back from the server,
    * the sentence will be displayed and response buttons indicating whether
    * or not the user liked it will appear.
    */
    function getSentence() {
        $("#gen-sentence").hide();
        $("#gen-sentence-again").hide();
        $("#intro").hide();
        $("#response-container").show();
        $("#sentence").removeData("typed");
        // $.get("http://localhost:3000/sentence", function(data) {
            $("#sentence").typed({
                // strings: [data.sentence],
                strings: ["I put a tuple in firebase."],
                typeSpeed: 0,
                showCursor: false
            });
            // setupFeedBackButtons(data.sentence);
            setupFeedBackButtons("I put a tuple in firebase.");
        // });
    }

    /**
    * Sets up the feedback buttons along with the appropriate onclick
    * listeners. 
    * @param sentence The sentence to be sent in a POST request if clicked on.
    */
    function setupFeedBackButtons(sentence) {
        $("#yes").show(); 
        $("#no").show(); 
        $("#yes").click({sentence: sentence, wasFunny : true}, reportResults);
        $("#no").click({sentence: sentence, wasFunny : false}, reportResults);
        $("#feedback").text("Did this impress your colleagues (or did you find it funny)?");
    }

    /**
    * Sends a POST request to the server with information about
    * the sentence and whether or not the user thought the sentence
    * was funny.
    * @param params An object representing the sentence that is being reported and
    * whether or not the sentence was funny or not.
    */
    function reportResults(params) {
        $.post("http://localhost:3000/results", params.data, function(data) {
            $("#feedback").text("Thanks for the feedback! Generate another!");
            $("#yes").hide();
            $("#no").hide();    
            $("#gen-sentence-again").show();
            $("#gen-sentence-again").click(getSentence);
        });
    }

}());
