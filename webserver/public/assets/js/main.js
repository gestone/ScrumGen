(function() {

    "use strict";

    var HEIGHT_SCALE = 5;
    var WINDOW_CUTOFF = 1000; // to rescale properly for mobile devices
    var HOST = "localhost:8080";
    var SENTENCE = "";

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
        $("#feedback-container").hide();
        $("#sentence").removeData("typed");
        $.get("http://" + HOST + "/sentence", function(data) {
            data = JSON.parse(data);
            SENTENCE = data.sentence;
            $("#sentence").typed({
                strings: [data.sentence],
                typeSpeed: 0,
                showCursor: false,
                callback: setupFeedBackButtons
            });
        });
    }

    /**
    * Sets up the feedback buttons along with the appropriate onclick
    * listeners. 
    */
    function setupFeedBackButtons() {
        $("#feedback-container").show();
        $("#yes").show();
        $("#no").show();
        $("#yes").click({sentence: SENTENCE, wasFunny : true}, reportResults);
        $("#no").click({sentence: SENTENCE, wasFunny : false}, reportResults);
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
        $.post("http://" + HOST + "/sentence", params.data, function(data) {
            $("#feedback").text("Thanks for the feedback! Generate another!");
            $("#yes").off("click");
            $("#yes").hide();
            $("#no").off("click");
            $("#no").hide();    
            $("#gen-sentence-again").off("click");
            $("#gen-sentence-again").click(getSentence);
            $("#gen-sentence-again").show();
        });
    }

}());
