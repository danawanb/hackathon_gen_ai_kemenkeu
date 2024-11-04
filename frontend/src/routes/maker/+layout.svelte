<script>
    import {
        Navbar,
        NavBrand,
        NavLi,
        NavUl,
        NavHamburger,
        Button,
        Input,
    } from "flowbite-svelte";
    // import MonkeyImage from "../../monkeyz.png";
    $: activeUrl = $page.url.pathname;
    import { page } from "$app/stores";
</script>

<div class="sticky top-0">
    <Navbar>
        <NavBrand href="/">
            <!--        <img src={MonkeyImage} class="me-3 h-6 sm:h-9" alt="MonkeyForm logo" />-->
            <span
                class="self-center whitespace-nowrap text-xl font-semibold dark:text-white"
                >Project Alpha</span
            >
        </NavBrand>
        <div class="flex md:order-2">
            <NavHamburger />
        </div>
        <NavUl class="order-1" {activeUrl}>
            <NavLi href="/maker" active={activeUrl === "/maker"}>Main</NavLi>
            <NavLi href="/" active={activeUrl === "/create"}>Settings</NavLi>
            <NavLi href="/">Navbar</NavLi>
        </NavUl>
    </Navbar>
    <div class="border-b-2 border-gray-200 shadow-md"></div>
</div>
<slot></slot>
