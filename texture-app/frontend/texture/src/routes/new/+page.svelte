<script>
    import { tick, onMount } from "svelte";
    import SceneDrawing from "../../lib/SceneDrawing.svelte";
    
    let username = "Orakuru 2.1";
    let history = [];
    let inputValue = "";
    let element;
    let conversationId = Math.floor(Math.random() * 10000);
    let timeLeft = 300;
    let originalImage = {};
    let missingObjects = {};
    let isCorrect = false;
    let isThinking = true;

    let thinking = ""
    let yay = ""
    let wrong = ""

    function startTimer() {
        const interval = setInterval(() => {
            if (timeLeft > 0) {
                timeLeft--;
            } else {
                clearInterval(interval);
                window.location.href = '/';
            }
        }, 1000);
    }

    onMount(async () => {
        // console.log(characterImages);
        thinking = localStorage.getItem('thinking') || "avatar_placeholder.webp";
        yay = localStorage.getItem('yay') || "avatar_placeholder.webp";
        wrong = localStorage.getItem('wrong') || "avatar_placeholder.webp";
        
        await loadImage();
        startTimer();
    });

    async function loadImage() {
        try {
            const data = {
                class_mask_pairs: {
                    "chair": "/mask_images/mask_chair.png",
                    "couch": "/mask_images/mask_couch.png",
                    "keyboard": "/mask_images/mask_keyboard.png",
                    "tv": "/mask_images/mask_tv.png"
                },
                original_image: "/mask_images/room_orig.png",
                status: "success"
            };
            conversationId = data.conversation_id;
            missingObjects = data.class_mask_pairs;
            originalImage = data.original_image;
            console.log(`Missing objects: ${Object.keys(missingObjects)}`);
        } catch (error) {
            console.error("Error sending message:", error);
            history = [...history, { message: "Sorry, I encountered an issue. Try again!", user: false }];
        }
    }
    
    async function sendMessage() {
        if (inputValue.trim() === "") return;

        history = [...history, { message: inputValue, user: true }];
        await tick();
        scrollToBottom(element);
        const value = inputValue
        inputValue = ""
        isThinking = true

        try {
            const response = await fetch('http://localhost:8000/api/ai_proxy/chat/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    message: `${value} $ ${JSON.stringify(missingObjects)}`,
                    conversation_id: conversationId
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            conversationId = data.conversation_id;
            history = [...history, { message: data.response, user: false }];
            console.log(data.response);
            

            if (data.response.toLowerCase().includes('congratulations') || 
                data.response.toLowerCase().includes('well') ||
                data.response.toLowerCase().includes('excellent') ||
                data.response.toLowerCase().includes('great')) {
                    console.log('Correct guess');
                    
                
                for (const obj of Object.keys(missingObjects)) {
                    console.log(`Missing Objects ${missingObjects}`)
                    if (value.toLowerCase().includes(obj)) {
                        delete missingObjects[obj];
                        console.log(`Removed ${obj} from missingObjects`);
                        isCorrect = true;
                    }
                }

               
                isThinking = false;
            } else {
                isCorrect = false;
            }
            isThinking = false;
        } catch (error) {
            console.error("Error sending message:", error);
            history = [...history, { message: "Sorry, I encountered an issue. Try again!", user: false }];
        }

        inputValue = "";
        await tick();
        scrollToBottom(element);
    }

    function scrollToBottom(node) {
        node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
    }

    function exit() {
        window.location.href = '/'
    }
</script>

<div class="container">
    <header>
        <h1>TEXTURE</h1>
        <div class="timer">Time Left: {timeLeft > 0 ? `${Math.floor(timeLeft / 60)}:${String(timeLeft % 60).padStart(2, '0')}` : "Time's up!"}</div>
        <div class="buttons">
            <!-- <button class="save">Save Game</button>
            <button class="save-exit">Save & Exit</button> -->
            <button class="exit" on:click={exit}>End Adventure</button>
        </div>
    </header>

    <main>
        <div class="sidebar floating-box">
            <!-- <div class="image-placeholder"></div> -->
             <SceneDrawing masks={missingObjects} original={originalImage}/>
             <div class="floating-image">
                {#if !isThinking}
                <img src={thinking}  class="feedback-image"/>
                {:else if isCorrect}
                <img src={yay} class="feedback-image"/>
                {:else if !isCorrect}
                <img src={wrong} class="feedback-image"/>
                {:else}
                <img src={thinking} class="feedback-image"/>
                {/if}
            </div>
        </div>
        <div class="content floating-box">
            <div class="tab-header">
                {username}
            </div>
            <div class="history" bind:this={element}>
                {#each history as item}
                    {#if item.user}
                        <div class="message user">{item.message}</div>
                    {:else}
                        <div class="message">{item.message}</div>
                    {/if}
                {/each}
            </div>
            <div class="text-content">
                <div class="input-box">
                    <textarea bind:value={inputValue} placeholder="Type your message here..."></textarea>
                    <button class="send-button" on:click={sendMessage}>▶</button>
                </div>
            </div>
        </div>
        
    </main>
</div>

<style>
    * {
        color: #333;
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 0;
    }

    .container {
        font-family: sans-serif;
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
        background: url('background.png') no-repeat center center fixed;
        background-size: cover;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        padding-top: 0;
        padding-bottom: 0;
        background: rgba(206, 223, 210, 0.9);
        border-radius: 10px;
        margin: 10px;
        margin-bottom: -10;
        margin-top: 0;
        height: 10%;
    }

    .buttons {
        display: flex;
        gap: 0.5em;
    }

    .buttons button {
        padding: 9px 18px;
        font-weight: bold;
        color: white;
        border: none;
        border-radius: 5px;
    }

    .save { background: #2543ec; }
    .save-exit { background: #0c2166; }
    .exit { background: #FF6B6B; }

    .floating-box {
        background: rgba(255, 255, 255, 1);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .floating-image {
        position: absolute; /* Floating over SceneDrawing */
        bottom: 5%; /* Adjust based on how much space you need */
        left: 10%; /* Move to the corner, adjust as needed */
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .feedback-image {
        width: 70%; /* Adjust as needed */
        opacity: 0.9;
        filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.5));
    }

    .sidebar {
        width: 60%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .image-placeholder {
        width: 600px;
        height: 700px;
        background: #c4c4c4;
        border-radius: 10px;
        background-image: url('download.jpg');
        background-position: center;
        background-size: cover;
    }

    main {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 40px;
        flex-grow: 1;
        padding: 10px;
        margin-top: -10px;
        margin-left: 20px;
        margin-right: 20px;
        margin-bottom: 20px;
        overflow: hidden; /* Prevents scrolling on main */
    }

    .content {
        width: 40%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        overflow: hidden; /* Prevents the content from pushing the main div */
    }

    .history {
        overflow-y: auto; /* Enables scrolling within history */
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        gap: 1em;
        padding: 10px;
        max-height: 60vh; /* Ensures it doesn’t expand indefinitely */
    }

    .tab-header {
        font-weight: bold;
        font-size: 1.5em;
        padding: 10px;
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.9);
    }

    .message, .user {
        max-width: 70%;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        backdrop-filter: blur(5px);
    }

    .message {
        background: rgba(32, 102, 231, 0.8);
        color: white;
    }

    .user {
        background: rgba(59, 117, 88, 0.8);
        margin-left: auto;
        color: white;
    }

    .text-content {
        width: 100%;
        display: flex;
        position: relative;
        padding-top: 10px;
    }

    .input-box {
        display: flex;
        align-items: center;
        background: rgba(55, 169, 223, 0.9);
        padding: 10px;
        border-radius: 10px;
        width: 100%;
        box-shadow: 0 0 10px rgba(54, 38, 139, 0.9);
    }

    textarea {
        flex: 1;
        resize: none;
        border: none;
        border-radius: 5px;
        background: white;
        padding: 10px;
        font-size: 1em;
    }

    .send-button {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
    }

    .timer {
        font-weight: bold;
        font-size: 2em;
        padding: 5px 10px;
        border-radius: 5px;
        margin-left: 55%;
    }

    .reset-timer {
        background: #4caf50;
        color: white;
        padding: 8px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
</style>