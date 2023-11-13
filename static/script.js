function tweetQuote() {
    const quote = document.getElementById('tweet').innerText;;
    console.log(quote)
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(quote)}`;
    window.open(twitterUrl, '_blank');
}