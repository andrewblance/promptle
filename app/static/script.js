function tweetQuote() {
    const quote = "hello world";
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(quote)}`;
    window.open(twitterUrl, '_blank');
}