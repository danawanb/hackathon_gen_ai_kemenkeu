/** @type {import('../../../../../.svelte-kit/types/src/routes').PageServerLoad} */
import { env } from '$env/dynamic/private'


export async function load() {
	let url = env.API_BASE_URL
	return {
		url,
	}

}
