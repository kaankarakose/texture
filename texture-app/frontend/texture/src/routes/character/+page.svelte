<script>
    import { onMount } from 'svelte';
    import { characterImages } from '../../lib/storage';
    let inputValue = "";
    let characterImagesLocal = {
        initial_pose: "avatar_placeholder.webp",
        thinking: "avatar_placeholder.webp",
        wrong: "avatar_placeholder.webp",
        yay: "avatar_placeholder.webp"
    };

    
    async function generateCharacter() {
        if (inputValue.trim() === "") return;
        
        try {
            const response = await fetch('http://localhost:8000/api/ai_proxy/comfy/generate-poses/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ prompt: inputValue }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update characterImages with received images
            Object.keys(characterImagesLocal).forEach(key => {
                if (data[key]) {
                    characterImagesLocal[key] = `data:image/jpeg;base64,${data[key]}`;
                    console.log(characterImagesLocal);
                    
                }
            });
        } catch (error) {
            console.error("Error generating character:", error);
        }
    }

    function back() {
        window.location.href = '/';
    }

    function finalizeCharacter() {
        console.log("Character finalized with prompt:", inputValue);
        for (const key of Object.keys(characterImages)) {
            localStorage.setItem(key, characterImagesLocal[key])
        }
        window.location.href = 'new'
    }
</script>

<div class="container">
    <header>
        <h1>Character Generator</h1>
    </header>

    <main>
        <div class="character-preview">
            <!-- {#each Object.keys(characterImages) as key}
                <img src={characterImages[key]} alt={key} class="image-preview">
            {/each} -->
            <img src={characterImagesLocal['initial_pose']} alt={'initial_pose'} class="image-preview">
        </div>
        <div class="text-content">
            <div class="input-box">
                <textarea bind:value={inputValue} placeholder="Type your message here..."></textarea>
                <button class="send-button" on:click={generateCharacter}>▶</button>
            </div>
        </div>
        <div class="buttons">
            <button class="back" on:click={back}>Back</button>
            <button class="finalize" on:click={finalizeCharacter}>Finalize Character</button>
        </div>
    </main>
</div>

<style>
    * { color: #333; box-sizing: border-box; }
    body { margin: 0; padding: 0; }
    
    .container {
        font-family: sans-serif;
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: url('background.png') no-repeat center center fixed;
        background-size: cover;
    }

    header {
        text-align: center;
        padding: 10px;
        background: rgba(206, 223, 210, 0.9);
        border-radius: 10px;
        margin: 10px;
    }
    
    .character-preview {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        width: 100%;
        margin: 20px 0;
    }

    .image-preview {
        width: 200px;
        height: 200px;
        border-radius: 10px;
        object-fit: cover;
        border: 2px solid #555;
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
        gap: 1em;
        width: 100%;
        box-shadow: 0 0 10px rgba(54, 38, 139, 0.9);
        justify-content: space-between;
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

    .buttons {
        display: flex;
        width: 100%;
        gap: 2em;
        margin-top: 2em;
        justify-content: space-around;
    }

    .buttons button {
        padding: 10px 20px;
        font-weight: bold;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .back { background: #777; }
    .submit { background: #2543ec; }
    .finalize { background: #4CAF50; }
</style>