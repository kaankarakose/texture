<script>
    import { onMount } from 'svelte';
  
    onMount(() => {
      console.log("SvelteKit app initialized!");
    });
  </script>
  
  <slot />