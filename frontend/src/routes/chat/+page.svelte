<script>
	import { Input, Button, Spinner, Label, Modal } from "flowbite-svelte";
	import { SearchOutline } from "flowbite-svelte-icons";
	import Header from "$lib/Header.svelte";
	import axios from "axios";
	import toast, { Toaster } from "svelte-french-toast";
	let show = false;
	let email;
	let ress;
	let loading = false;
	//import fasilitas from "../../assets/busak_ai_image.png";
	import { onMount } from "svelte";
	export let data;

	onMount(() => {});

	let unix = "";
	let cariModal = false;
	let formModal = false;

	let tmt = new Date();
	import { goto } from "$app/navigation";

	let simpanHeader = async () => {
		loading = true;
		try {
			let res = await axios.post(
				data.url + `/busak_ai/insert_usage/`,
				{
					email: email,
				},
				{ withCredentials: true },
			);

			console.log(res.data);
			toast.success(
				`Berhasil daftar email, silahkan cek email anda :)`,
			);
			setTimeout(() => {
				loading = false;
				formModal = false;
				// goto(`/fasilitas/diantemi_terbuka/${res.data.data}`)
			}, 200);
		} catch (e) {
			console.log(e);
			toast.error(e.response.data.message.toString());
			loading = false;
		}
	};

	let token;
</script>

<Header />
<div class="xl:mr-[5%] xl:ml-[5%] sm:mx-4 mt-28 sm:mt-36 mb-28 sm:ml-2">
	<img
		class="xl:max-w-3xl sm:max-w-xl mx-auto"
		src="https://gw.alipayobjects.com/mdn/rms_08e378/afts/img/A*P0S-QIRUbsUAAAAAAAAAAABkARQnAQ"
		alt="gambar Chat"
	/>
	<Toaster />
	<div class="items-center mb-12 mt-12 max-w-4xl mx-auto">
		<p
			class="xl:mx-36 sm:mx-4 items-center text-center font-bold text-2xl dark:text-white mb-4 text-blue-900"
		>
			Knowledge Base Chat
		</p>
		<p
			class="xl:mx-36 sm:mx-4 items-center text-center font-light text-sm dark:text-white mb-4 text-gray-600"
		>
			Fitur ini dapat digunakan tetapi masih dalam versi alpha
		</p>
		<div class="mb-4 xl:mx-72 text-center">
			<Button
				slot="right"
				size="sm"
				type="submit"
				class="mr-4"
				on:click={() => {
					formModal = true;
				}}>Daftar Email</Button
			>
			<Button
				slot="right"
				size="sm"
				type="submit"
				on:click={() => {
					cariModal = true;
				}}
				color="yellow">Masukan Token</Button
			>
		</div>
		<Modal
			bind:open={formModal}
			size="md"
			autoclose={false}
			class="w-full"
		>
			<form class="flex flex-col space-y-6" action="#">
				<h3
					class="mb-4 text-xl font-medium text-gray-900 dark:text-white"
				>
					Daftarkan email anda untuk mendapatkan
					token
				</h3>
				<div>
					<Label class="space-y-2">
						<span>Email</span>
						<Input
							type="text"
							name="email"
							placeholder="Isikan Email anda"
							bind:value={email}
							required
						/>
					</Label>
				</div>
				{#if loading}
					<Button class="w-24">
						<Spinner
							class="mr-1 "
							size="4"
							color="white"
						/>
					</Button>
				{:else}
					<Button
						type="submit"
						class="w-36"
						on:click={() => {
							simpanHeader();
						}}>Simpan</Button
					>
				{/if}
				<div
					class="text-sm font-medium text-gray-500 dark:text-gray-300"
				>
					Warning ! Anda akan mendapatkan email
					balasan yang berisi token untuk
					mengakses chat dengan Buku Saku AI
				</div>
			</form>
		</Modal>
	</div>
</div>
