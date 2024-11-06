<script>
	import {
		Card,
		Button,
		Skeleton,
		Dropdown,
		DropdownItem,
		Modal,
		Textarea,
		Spinner,
		Label,
	} from "flowbite-svelte";
	import {
		AngleLeftOutline,
		ChevronDownOutline,
		ExclamationCircleOutline,
		ThumbsDownSolid,
		ThumbsUpSolid,
	} from "flowbite-svelte-icons";
	import { toast, Toaster } from "svelte-french-toast";
	import { goto } from "$app/navigation";
	import Header from "$lib/Header.svelte";
	import { DataHandler, Datatable } from "@vincjo/datatables";
	import axios from "axios";
	import Select from "svelte-select";
	import { onMount } from "svelte";
	export let data;
	let handler;
	let delete_modal = false;
	let update_modal = false;
	let current_update_text = "";
	let rows;
	let current_ids;
	let delete_loading = false;
	let current_pertanyaan = "";
	let current_jawaban = "";
	let current_ids_list;

	onMount(async () => {
		await get_data_eval();
	});

	let scroll_into_view = ({ target }) => {
		const el = document.querySelector(target.getAttribute("href"));
		if (!el) return;
		el.scrollIntoView({
			behavior: "smooth",
		});
	};

	let loading = false;
	let get_data_eval = async () => {
		try {
			loading = true;
			let res = await axios.get(
				data.url +
					"/api/eval/get_eval?status=" +
					pilihan_val.value,
				{ withCredentials: true },
			);
			handler = new DataHandler(res.data, {
				rowsPerPage: 10,
			});
			rows = handler.getRows();
			loading = false;
		} catch (e) {
			loading = false;
			console.log(e);
		}
	};
	let handle_delete = async () => {};

	let pilihan = [
		{ value: 0, label: "Belum" },
		{ value: 1, label: "Sudah" },
	];

	let pilihan_val = { value: 0, label: "Belum" };

	let insert_eval = async (ids_list, ids_eval, pertanyaan, jawaban) => {
		try {
			let page_content = "";
			if (pertanyaan.includes("?")) {
				page_content = pertanyaan + " " + jawaban;
			} else {
				page_content = pertanyaan + "? " + jawaban;
			}
			let datax = {
				ids_list: ids_list,
				page_content: page_content,
				ids_eval: ids_eval,
			};
			await axios.post(
				data.url + "/api/eval/insert_eval",
				datax,
				{ withCredentials: true },
			);
			toast.success("berhasil input evaluasi");
		} catch (e) {
			console.log(e);
			toast.error(e.data.detail);
		}
	};
</script>

<Header />
<div class="mx-12 mt-12">
	<Toaster />
	<Button
		class="mr-2"
		on:click={() => {
			goto("/maker");
		}}
		><AngleLeftOutline
			size="xs"
			class="mr-1 text-white dark:text-white"
		/>Kembali</Button
	>
</div>
<div class="mx-12 mt-6 grid grid-cols-4 gap-4">
	<div>
		<Card
			img="https://api.tinycode.cloud/api/maker/image/0390e848-6763-4b7a-93f1-12c802474415.webp"
			alt="https://api.tinycode.cloud/api/maker/image/0390e848-6763-4b7a-93f1-12c802474415.webp"
			class="max-h-45"
		>
			<h5
				class="mb-4 text-lg font-bold tracking-tight text-gray-900 dark:text-white"
			>
				Daftar Feedback
			</h5>
			<a
				class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
				href="#section-1"
				on:click|preventDefault={scroll_into_view}
			>
				Details
			</a>
		</Card>
	</div>
	<div>
		<Card
			img="https://turso.tech/_next/image?url=%2Fimages%2Fblog%2Fdatabases-have-traditionally-been-expensive-what-if-we-could-change-that-ec7f32ab%2Fcover.png&w=3840&q=100"
			alt="image camera"
			class="max-h-45"
		>
			<h5
				class="mb-4 text-lg font-bold tracking-tight text-gray-900 dark:text-white"
			>
				Rekap Pertanyaan dan Jawaban
			</h5>
			<a
				class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
				href="#section-2"
				on:click|preventDefault={scroll_into_view}
			>
				Details
			</a>
		</Card>
	</div>
</div>
<div class="mt-24 mx-12">
	<section id="section-1">
		<div class="mb-4">
			<Label for="title" class="block mb-2">Kategori</Label>
			<Select
				class="mt-2"
				items={pilihan}
				on:change={get_data_eval}
				bind:value={pilihan_val}
				placeholder="Pilih kategori"
			/>
		</div>
		{#if handler}
			<Datatable
				{handler}
				class="border border-gray-150 rounded-lg px-2 py-2 mb-6"
			>
				<table class=" mt-4">
					<thead class="display mt-4">
						<tr>
							<th class="w-4">No</th>
							<th class="w-[20%]"
								>Pertanyaan</th
							>
							<th class="w-[40%]"
								>Jawaban</th
							>
							<th class="w-4"
								>Feedback</th
							>

							<th class="w-2"
								>Action</th
							>
						</tr>
					</thead>
					<tbody class="border-2">
						{#each $rows as row, i}
							<tr>
								<td
									class="p-[4px] text-center border border-gray-150 hover:bg-gray-100"
									>{i +
										1}</td
								>
								<td
									class="p-[4px] border border-gray-150 hover:bg-gray-100"
									><p
										class="whitespace-pre-wrap"
									>
										{row.pertanyaan}
									</p></td
								>
								<td
									class="p-[4px] border border-gray-150 hover:bg-gray-100"
									><p
										class="whitespace-pre-wrap"
									>
										{row.jawaban}
									</p></td
								>
								<td
									class="p-[4px] border border-gray-150 hover:bg-gray-100 items-center text-center"
								>
									{#if row.feedback == 1}
										<Button
											color="red"
											size="xs"
										>
											<ThumbsDownSolid
												class="w-3 h-3 text-white"
											/></Button
										>
									{:else}
										<Button
											color="blue"
											size="xs"
										>
											<ThumbsUpSolid
												class="w-3 h-3 text-white"
											/></Button
										>
									{/if}
								</td>
								<td
									class="p-[4px] text-center border border-gray-150 hover:bg-gray-100"
								>
									<Button
										>Action<ChevronDownOutline
											class="w-6 h-6 ms-2 text-white dark:text-white"
										/></Button
									>
									<Dropdown
									>
										<DropdownItem
											on:click={async () => {
												update_modal = true;
												current_ids =
													row.ids;
												current_ids_list =
													row.ids_list;
												current_pertanyaan =
													row.pertanyaan;
												current_jawaban =
													row.jawaban;
											}}
											>Evaluasi</DropdownItem
										>
									</Dropdown>
								</td></tr
							>
						{/each}
						<Modal
							bind:open={delete_modal}
							size="xs"
							autoclose
						>
							<div
								class="text-center"
							>
								<ExclamationCircleOutline
									class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200"
								/>
								<h3
									class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400"
								>
									Apakah
									yakin
									akan
									menghapus
									ini ? {current_ids}
								</h3>
								{#if delete_loading}
									<Button>
										<Spinner
											class="me-3"
											size="4"
											color="white"
										/>
										Loading
										...
									</Button>
								{:else}
									<Button
										color="red"
										class="me-2"
										on:click={handle_delete}
										>Ya</Button
									>
									<Button
										color="alternative"
										on:click={() =>
											(delete_modal = false)}
										>Tidak</Button
									>
								{/if}
							</div>
						</Modal>
						<Modal
							title="Update Knowledge"
							bind:open={update_modal}
							size="xl"
						>
							<Textarea
								class="h-96"
								bind:value={current_jawaban}
							></Textarea>

							<svelte:fragment
								slot="footer"
							>
								<Button
									on:click={async () => {
										await insert_eval(
											current_ids_list,
											current_ids,
											current_pertanyaan,
											current_jawaban,
										);
									}}
									>Simpan</Button
								>
								<Button
									color="alternative"
									on:click={() =>
										(update_modal = false)}
									>Batal</Button
								>
							</svelte:fragment>
						</Modal>
					</tbody>
				</table>
			</Datatable>
		{:else}
			<Skeleton size="xxl" class="mt-8 mb-2.5" />
			<Skeleton size="xxl" class="mt-8 mb-2.5" />
			<Skeleton size="xxl" class="mt-8 mb-2.5" />
		{/if}
	</section>
	<section id="section-2">
		<h2>Section 2</h2>
	</section>

	<section id="section-3">
		<h2>Section 3</h2>
	</section>
</div>

<style>
	section {
		min-height: 100vh;
	}
</style>
