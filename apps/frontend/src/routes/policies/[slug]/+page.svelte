<script lang="ts">
  export let data;
</script>

<section class="mx-auto max-w-3xl px-4 py-10">
  <h2 class="font-display text-3xl mb-4">{data.page.title}</h2>
  <div class="prose prose-invert max-w-none" this={el => el && (el.innerHTML = data.page.html_content)} />
</section>