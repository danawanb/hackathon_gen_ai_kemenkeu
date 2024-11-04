<script lang="ts">
	import { Alert, Blockquote, Card } from "flowbite-svelte";
	import Header from "$lib/Header.svelte";
	import { Button, Spinner } from "flowbite-svelte";
	import {
		ArrowRightOutline,
		CheckCircleSolid,
	} from "flowbite-svelte-icons";
	import axios from "axios";
	export let data;
	import { toast } from "svelte-french-toast";
	let daftar = ["Gratis", "Premium"];
	import { goto } from "$app/navigation";
	import Cookies from "js-cookie";

	let loading = false;
	let handle_demo = async () => {
		loading = true;
		await axios
			.get(data.url + `/api/user/set_token`, {
				withCredentials: true,
			})
			.then((response) => {
				loading = false;
				Cookies.set("user_69", response.data, {
					expires: 1,
				});
				goto("/maker");
			})
			.catch((err) => {
				toast.error(err.response.data.detail);
				loading = true;
				console.log(err);
			});
	};
</script>

<div class="bg-blue-600 dark:bg-gray-800">
	<Header />

	<div class="flex flex-row mt-8">
		<div class="ml-24">
			<video
				src="https://www.typeform.com/static/homepage/hero/hero.webm"
				class="mx-auto xl:max-w-xl"
				muted
				autoplay
				loop
			/>
		</div>
		<div class="ml-24 mt-36 mb-12">
			<h1
				class="text-white text-5xl font-extrabold max-w-2xl"
			>
				Enhanced your knowledge about Government
				Treasury ✨
			</h1>
			<h1 class="text-white text-xl mt-4 max-w-2xl">
				TreasuryAI let's you to understand about
				government treasury quickly and easily.
			</h1>
			<div class="mt-4">
				<a
					href="https://api.tinycode.cloud/api/user/auth/google"
					><Button
						color="alternative"
						size="lg"
						class="mr-2"
						pill
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="w-4 h-4 mr-2"
							viewBox="0 0 48 48"
						>
							<path
								fill="#FFC107"
								d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"
							></path><path
								fill="#FF3D00"
								d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"
							></path><path
								fill="#4CAF50"
								d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"
							></path><path
								fill="#1976D2"
								d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"
							></path>
						</svg>
						Continue With Google <ArrowRightOutline
							class="w-5 h-5 ms-2"
						/></Button
					></a
				>
				{#if loading}
					<Button color="yellow">
						<Spinner
							class="me-3"
							size="4"
							color="white"
						/>Loading ...
					</Button>
				{:else}
					<Button
						color="yellow"
						pill
						size="lg"
						on:click={handle_demo}
					>
						Demo
					</Button>
				{/if}
			</div>
			<p class="text-white text-xs mt-1 max-w-2xl italic">
				Google Login currently in development
			</p>
		</div>
	</div>
	<div class="bg-white dark:bg-gray-700">
		<div class="h-36 bg-white mt-12 dark:bg-gray-700 py-5">
			<Blockquote
				size="xl"
				class="max-w-4xl mt-4 justify-center text-center mx-auto text-blue-900"
				>"With a focus on simplicity and speed, it's
				perfect for anyone needing fast, hassle-free
				form creation"</Blockquote
			>
		</div>
		<div class=" bg-white dark:bg-gray-700">
			<Card class="mx-auto"></Card>
		</div>
		<div
			class="bg-white dark:bg-gray-700 flex flex-row mx-auto gap-2 items-center justify-center mb-12"
		>
			{#each daftar as daf}
				<Card padding="lg" class="mx-4">
					<h5
						class="mb-4 text-xl font-medium text-gray-500 dark:text-gray-400"
					>
						{daf}
					</h5>
					<div
						class="flex items-baseline text-gray-900 dark:text-white"
					>
						<span
							class="text-3xl font-extrabold tracking-tight"
							>Free</span
						>
						<span
							class="ms-1 text-xl font-normal text-gray-500 dark:text-gray-400"
							>/month</span
						>
					</div>
					<!-- List -->
					<ul class="my-7 space-y-4">
						<li
							class="flex space-x-2 rtl:space-x-reverse"
						>
							<CheckCircleSolid
								class="w-4 h-4 text-primary-600 dark:text-primary-500"
							/>
							<span
								class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400"
							>
								20 Form per
								bulan
							</span>
						</li>
						<li
							class="flex space-x-2 rtl:space-x-reverse"
						>
							<CheckCircleSolid
								class="w-4 h-4 text-primary-600 dark:text-primary-500"
							/>
							<span
								class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400"
							>
								Jumlah isian
								tidak terbatas
							</span>
						</li>
						<li
							class="flex space-x-2 rtl:space-x-reverse"
						>
							<CheckCircleSolid
								class="w-4 h-4 text-primary-600 dark:text-primary-500"
							/>
							<span
								class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400"
							>
								Link
							</span>
						</li>
						<li
							class="flex space-x-2 rtl:space-x-reverse"
						>
							<CheckCircleSolid
								class="w-4 h-4 text-primary-600 dark:text-primary-500"
							/>
							<span
								class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400"
							>
								Custom URL By
								Default
							</span>
						</li>
					</ul>
				</Card>
			{/each}
		</div>
	</div>
</div>
