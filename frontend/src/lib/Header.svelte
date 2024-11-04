<script lang="ts">
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
	} from "flowbite-svelte";
	import { DarkMode } from "flowbite-svelte";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
	//import MonkeyLogo from "../../monkeyz.png";
	import { onMount } from "svelte";
	let MonkeyLogo =
		"https://w7.pngwing.com/pngs/826/876/png-transparent-chimpanzee-logo-monkey-ape-monkey-face-animals-head-thumbnail.png";
	$: activeUrl = $page.url.pathname;
	let scrolled = false;

	const handleScroll = () => {
		scrolled = window.scrollY > 50; // Ubah 50 sesuai jarak yang kamu inginkan
	};
	onMount(() => {
		window.addEventListener("scroll", handleScroll);

		// Hapus event listener saat komponen di-destroy
		return () => {
			window.removeEventListener("scroll", handleScroll);
		};
	});
</script>

<Navbar
	on:scroll={handleScroll}
	let:NavContainer
	class="sticky top-0 transition-bg {scrolled
		? 'bg-transparent'
		: 'bg-blue-600'} dark:bg-gray-800 p-4 text-white"
>
	<NavContainer
		class="px-5 py-2 xl:rounded-full sm:rounded-xl md:rounded-xl bg-white/20  shadow-lg ring-1 ring-black/5  dark:bg-gray-600 max-w-6xl"
	>
		<NavBrand href="/">
			<img
				src={MonkeyLogo}
				class="me-3 h-8 sm:h-9"
				alt="Flowbite Logo"
			/>
			<span
				class="self-center whitespace-nowrap text-xl font-semibold text-gray-300"
				>Project Alpha</span
			>
		</NavBrand>
		<NavHamburger />
		<NavUl>
			<NavLi
				href="/"
				class="text-gray-300 hover:underline hover:font-bold"
				>Home</NavLi
			>
			<NavLi
				href="/"
				class="text-gray-300 hover:underline hover:font-bold"
				>About</NavLi
			>

			<NavLi
				href="/"
				class="text-gray-300 hover:underline hover:font-bold"
				on:click={() => {
					goto("/chat");
				}}>Chat</NavLi
			>
		</NavUl>
		<!--		<DarkMode class="text-white hover:bg-gray-200" />-->
	</NavContainer>
</Navbar>

<style>
	.transition-bg {
		transition: background-color 0.3s ease;
	}
</style>
