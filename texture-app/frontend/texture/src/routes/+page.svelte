<script>
    import Navbar from "$lib/Navbar.svelte";
</script>

<Navbar/>

<div class="content">
  <div class="text-container">
      <h1>Texture</h1>
      <h3>Unravel new adventures, one twist at a time.</h3>
      <p>A text-driven adventure game guided by an AI companion</p>
  </div>

  <div class="button-container">
      <!-- <a class="continue-adventure" href="character">Continue</a> -->
      <a class="primary" href="character">New Adventure</a>
      <a class="secondary">How to Play</a>
  </div>
</div>

<style>
  /* Full-page layout with no scrollbars */
  html, body, #app {
    margin: 0;
    padding: 0;
    height: 100vh;
    width: 100vw;
    overflow: hidden; 
    display: flex;
    flex-direction: column;
  }

  /* Fullscreen background */
  .content {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    /* justify-content: space-between; // Distributes content evenly */
    gap: 27%;
    align-items: center;
    background-image: url('background.png'); /* Ensure it's in 'public/' */
    background-size: cover;
    background-position: center;
    padding-top: 5vh; /* Moves text up */
    padding-bottom: 10vh; /* Moves buttons down */
  }

  /* Text container */
  .text-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  h1 { 
    font-size: 8em;
    margin-bottom: -0.25em;
    color: #333;
    text-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
    font-family: "Sixtyfour", sans-serif;
    font-optical-sizing: auto;
    font-weight: 400;
    font-style: normal;
    font-variation-settings:
      "BLED" 0,
      "SCAN" 0;
    letter-spacing: -0.1em;
  }

  h3 {
    font-size: 3em;
    margin-bottom:-0.5em;
    color: #333;
  }

  p {
    font-size: 1.5em;
    max-width: 70%;
    color: #333;
  }

  /* Button container */
  .button-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    align-items: center;
  }

  a {
    width: 220px;
    padding: 14px 18px;
    font-size: 1.2em;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s ease-in-out;
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
    text-align: center;
  }

  .continue-adventure {
    background-color: #1C4D65;
    color: white;
    font-weight: bold;
  }

  .continue-adventure:hover {
    background-color: #0F3A4D;
  }

  .primary {
    background-color: #83AFAB;
    color: white;
    font-weight: bold;
  }

  .primary:hover {
    background-color: #6D9E9B;
  }

  .secondary {
    background-color: #B6CAC4;
    color: #333;
  }

  .secondary:hover {
    background-color: #A9BDB7;
  }
</style>
