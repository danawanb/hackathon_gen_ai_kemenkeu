import { writable } from 'svelte/store';

export const page_content_pdf = writable([]);
export const file_content_pdf = writable();
export let metadatas = writable();
export let file_name = writable("");
