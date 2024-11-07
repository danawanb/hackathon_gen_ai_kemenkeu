<script>
    import {
        Button,
        ButtonGroup,
        Input,
        Span,
        Card,
        Dropdown,
        Li,
        Helper,
        InputAddon,
        Label,
        Modal,
        P,
        Mark,
        Spinner,
        Textarea,
        Accordion,
        Heading,
        AccordionItem,
        DropdownItem,
    } from "flowbite-svelte";
    import { onDestroy } from "svelte";
    import { tweened } from "svelte/motion";
    import * as easingFns from "svelte/easing";
    import { toast, Toaster } from "svelte-french-toast";
    import Header from "$lib/Header.svelte";
    import {
        ThumbsDownSolid,
        ThumbsUpSolid,
        BookSolid,
        ArrowRightOutline,
        ChevronRightOutline,
    } from "flowbite-svelte-icons";

    export let data;
    import axios from "axios";
    let urlServer = data.url;
    let token = data.slug;
    //let baseUrl = data.base_url;

    let easingName = "circInOut";
    let positionStore;
    let position = 0;
    let cleanup = null;

    onDestroy(() => {
        if (cleanup) cleanup();
    });

    let indexType = 0;
    let stopperIndex = 0;

    // @ts-ignore: Unreachable code error
    $: easing = easingFns[easingName];
    $: {
        if (cleanup) cleanup();

        positionStore = tweened(0, { easing, duration: 3000 });
        cleanup = positionStore.subscribe((val) => (position = val));

        positionStore.set(pertanyaan[indexType].message.length);
    }

    $: pertanyaan = [
        {
            message:
                "Halo saya adalah AI yang siap membantu anda menjawab pertanyaan menganai Keuangan Negara. Setujui syarat dan ketentuan terlebih dahulu sebelum mengajukan pertanyaan.",
            timestamp: Date.now(),
            user: "ai",
            sender: "AI",
            docs: [],
            toggled: false,
            image: "https://miro.medium.com/v2/resize:fit:1024/1*pZcSPPuXUpUrzq05OVJuHA.jpeg",
        },
    ];

    let valInput;
    let loading = false;

    let inputMessage = async () => {
        if (setuju === false) {
            return;
        }

        if (valInput.length < 10) {
            toast.error("Pastikan bertanya secara lengkap");
            return;
        }
        loading = true;
        stopperIndex += 2;
        console.log(stopperIndex);

        let mes = {
            message: valInput,
            timestamp: Date.now(),
            user: "human",
            sender: "sender",
            toggled: false,
            image: "https://as2.ftcdn.net/v2/jpg/05/76/65/21/1000_F_576652189_WK1JiTOwjKCFIJDJJLI1Q6RtwSfpgspu.jpg",
        };
        pertanyaan = [...pertanyaan, mes];

        header_pernyataan = true;
        let res = await postMessage(valInput);
        //console.log(res);

        if (res == null) {
            toast.error("Tidak ada data");
            indexType += 2;
            valInput = "";
            loading = false;
            return;
        }
        if (res !== "") {
            let text = res.res;
            let contains = text.toLowerCase().includes("maaf");

            if (contains) {
                let mes2 = {
                    message: res.res,
                    timestamp: Date.now(),
                    user: "ai",
                    sender: "AI",
                    toggled: true,
                    docs: [],
                    ids_list: res.ids_list,
                    image: "https://miro.medium.com/v2/resize:fit:1024/1*pZcSPPuXUpUrzq05OVJuHA.jpeg",
                };
                pertanyaan = [...pertanyaan, mes2];
            } else {
                let mes2 = {
                    message: res.res,
                    timestamp: Date.now(),
                    user: "ai",
                    sender: "AI",
                    toggled: true,
                    docs: res.files,
                    ids_list: res.ids_list,
                    aturan: res.detail,
                    image: "https://miro.medium.com/v2/resize:fit:1024/1*pZcSPPuXUpUrzq05OVJuHA.jpeg",
                };
                pertanyaan = [...pertanyaan, mes2];

                await postRekap(valInput, res.res, res.ids_list);
            }
        }

        indexType += 2;
        valInput = "";
        loading = false;
    };

    let postMessage = async (val) => {
        try {
            let datax = {
                question: val,
            };
            let response = await axios.post(
                data.url + "/api/chat/do_answer",
                datax,
                { withCredentials: true },
            );

            return response.data;
        } catch (e) {
            loading = false;
            return null;
        }
    };

    let defaultModal = false;

    let setuju = false;

    let postEvaluasi = async (per, jwb, status, ids_list) => {
        try {
            const response = await fetch(urlServer + "/api/chat/insert_eval", {
                method: "POST", // *GET, POST, PUT, DELETE, etc.
                cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
                credentials: "include", // include, *same-origin, omit
                headers: {
                    "Content-Type": "application/json",
                    // 'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: JSON.stringify({
                    pertanyaan: per,
                    jawaban: jwb,
                    feedback: status,
                    ids_list: ids_list,
                }), // body data type must match "Content-Type" header
            });

            if (response.ok) {
                toast.success(
                    "Berhasil simpan evaluasi atas pertanyaan dan jawaban. Terima kasih 🥰",
                );
                return await response.json();
            }
        } catch (e) {
            toast.error(e.toString());
            console.log(e);
        }
    };

    let postRekap = async (per, jwb, ids_list) => {
        try {
            const response = await fetch(urlServer + "/api/chat/insert_recap", {
                method: "POST", // *GET, POST, PUT, DELETE, etc.
                cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
                credentials: "include", // include, *same-origin, omit
                headers: {
                    "Content-Type": "application/json",
                    // 'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: JSON.stringify({
                    pertanyaan: per,
                    jawaban: jwb,
                    ids_list: ids_list,
                }), // body data type must match "Content-Type" header
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            toast.error(e.toString());
            console.log(e);
        }
    };

    let imageModal = false;

    let pertanyaan_default = [
        "Apa itu IKPA (Indikator Kinerja Pelaksanaan Anggaran) ?",
        "Seperti apa prinsip belanja satuan kerja yang berkualitas ?",
        "Apa syarat penunjukan Pejabat Pembuat Komitmen ?",
        "Apa saja tugas Pejabat Pembuat Komitmen ?",
    ];
    let default_pertanyaan_modal = false;

    let header_pernyataan = true;
</script>

<svelte:window
    on:keydown={(e) => {
        switch (e.key) {
            case "Enter":
                inputMessage();
                break;
        }
    }}
/>
<Header />
<div class="mx-12 mt-12">
    <Toaster />
    {#if header_pernyataan}
        <div class="mx-4 mb-8">
            <Heading
                tag="h1"
                class="mb-2"
                customSize="text-2xl text-gray-700 font-extrabold  md:text-5xl lg:text-3xl"
            >
                Selamat
                <Span gradient>Pagi</Span>
                ☀️🪴🍳🧘‍♀️☕️
            </Heading>
            <h3 class="font-bold text-lg text-gray-700">
                Ajukan pertanyaanmu seperti di bawah ini atau gunakan
                pertanyaanmu sendiri
            </h3>
        </div>
        <div class="flex flex-row mx-4 mb-4">
            {#each pertanyaan_default as pertanyaan}
                <button
                    on:click={() => {
                        default_pertanyaan_modal = true;
                        valInput = pertanyaan;
                    }}
                >
                    <Card class="mr-6 max-w-xs hover:bg-gray-100">
                        <p
                            class="font-semibold h-20 text-lg text-gray-700 dark:text-gray-400 leading-tight"
                        >
                            {pertanyaan}
                        </p>
                    </Card>
                </button>
            {/each}
            <Modal
                title="Syarat dan Ketentuan"
                bind:open={default_pertanyaan_modal}
            >
                <p
                    class="text-base leading-relaxed text-gray-500 dark:text-gray-400"
                >
                    Fitur chat masih dalam tahap beta dan hanya tersedia untuk
                    informasi yang berkaitan dengan keuangan negara dan tidak
                    dapat dijadikan dasar hukum
                </p>
                <p
                    class="text-base leading-relaxed text-gray-500 dark:text-gray-400"
                >
                    Apabila terdapat jawaban yang salah harap kirimkan jawaban
                    tersebut menggunakan fitur kirim yang ada pada bagian kanan
                    tombol kanan chat
                </p>
                <svelte:fragment slot="footer">
                    <Button
                        on:click={async () => {
                            setuju = true;
                            console.log(valInput);
                            default_pertanyaan_modal = false;
                            header_pernyataan = false;
                            await inputMessage();
                            setuju = true;
                        }}>Setuju</Button
                    >
                    <Button
                        color="alternative"
                        on:click={() => {
                            setuju = false;
                        }}>Tidak Setuju</Button
                    >
                </svelte:fragment>
            </Modal>
        </div>
    {/if}
    <div class="mx-4 mt-6">
        <Button on:click={() => (defaultModal = true)} class="mr-2 mb-2"
            >Syarat dan Ketentuan</Button
        >
    </div>

    <Modal
        title="Bagaimana cara kerja treasuryAI"
        bind:open={imageModal}
        size="lg"
        autoclose
    >
        <img
            src="https://cdn.snorkel.ai/wp-content/uploads/2023/09/image3.png"
            alt="how rag works"
            class="xl:max-w-3xl sm:max-w-xl"
        />
    </Modal>
    <Modal title="Syarat dan Ketentuan" bind:open={defaultModal} autoclose>
        <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
            Fitur chat treasuryAI masih dalam tahap pengembangan dan hanya
            tersedia untuk informasi yang terbatas secara umum dan tidak dapat
            dijadikan dasar hukum
        </p>
        <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
            Apabila terdapat jawaban yang salah harap kirimkan jawaban tersebut
            menggunakan fitur kirim yang ada pada bagian kanan tombol kanan chat
            treasuryAI
        </p>
        <svelte:fragment slot="footer">
            <Button
                on:click={() => {
                    setuju = true;
                    header_pernyataan = false;
                }}>Setuju</Button
            >
            <Button
                color="alternative"
                on:click={() => {
                    setuju = false;
                }}>Tidak Setuju</Button
            >
        </svelte:fragment>
    </Modal>
    {#each pertanyaan as per, index}
        {#if per.user === "ai"}
            <div class="flex items-start gap-2.5 mt-12">
                <img
                    class="w-8 h-8 rounded-full ml-4"
                    src={per.image}
                    alt="Jese image"
                />
                <div
                    class="flex flex-col w-full leading-1.5 p-4 border-gray-200 bg-gray-200 rounded-e-xl rounded-es-xl dark:bg-gray-700 mr-4"
                >
                    <div
                        class="flex items-center space-x-2 rtl:space-x-reverse"
                    >
                        <span
                            class="text-sm font-semibold text-gray-900 dark:text-white"
                            >{per.sender}</span
                        >
                        <span
                            class="text-sm font-normal text-gray-500 dark:text-gray-400"
                            >{per.timestamp}
                        </span>
                        {#if index > 0}
                            {#if per.toggled}
                                <Button
                                    color="blue"
                                    size="xs"
                                    on:click={() => {
                                        per.toggled = false;
                                        postEvaluasi(
                                            pertanyaan[index - 1].message,
                                            per.message,
                                            0,
                                            per.ids_list,
                                        );
                                    }}
                                >
                                    <ThumbsUpSolid
                                        class="w-3 h-3 text-white"
                                    /></Button
                                >
                                <Button
                                    color="red"
                                    size="xs"
                                    on:click={() => {
                                        per.toggled = false;
                                        postEvaluasi(
                                            pertanyaan[index - 1].message,
                                            per.message,
                                            1,
                                            per.ids_list,
                                        );
                                    }}
                                >
                                    <ThumbsDownSolid
                                        class="w-3 h-3 text-white"
                                    /></Button
                                >
                            {/if}
                        {/if}
                    </div>
                    <p
                        class="whitespace-pre-wrap text-sm font-normal py-2.5 text-gray-900 dark:text-white"
                    >
                        {#if index === stopperIndex}
                            {per.message.substring(0, position)}
                        {:else}
                            {per.message}
                        {/if}
                    </p>
                    <div class="flex flex-row">
                        {#if per.docs.length > 0}
                            <div class="mt-2 mr-4">
                                <Button size="xs"
                                    ><BookSolid class="w-4 h-4 me-2" />Dokumen
                                    sumber</Button
                                >
                                <Dropdown class="w-60 p-3 space-y-1 text-sm">
                                    <DropdownItem
                                        class="rounded p-2 hover:bg-gray-100 dark:hover:bg-gray-600"
                                    >
                                        Peraturan
                                    </DropdownItem>
                                </Dropdown>
                            </div>
                        {/if}
                        {#if per.aturan}
                            <div class="mt-2">
                                <Button size="xs"
                                    ><BookSolid class="w-4 h-4 me-2" />Sumber
                                    Aturan</Button
                                >
                                <Dropdown class="w-60 p-3 space-y-1 text-sm">
                                    {#each per.aturan as atur}
                                        <DropdownItem
                                            class="flex items-center justify-between rounded p-2 hover:bg-gray-100 dark:hover:bg-gray-600"
                                        >
                                            {atur.aturan.pasal} - {atur.nomor}
                                            <ChevronRightOutline
                                                class="w-6 h-6 ms-2 text-primary-700 dark:text-white"
                                            />
                                        </DropdownItem>
                                        <Dropdown
                                            placement="right-start"
                                            class="max-w-full w-full relative"
                                        >
                                            <div class="max-w-full">
                                                <p class="text-sm max-w-full">
                                                    {atur.page_content}
                                                </p>
                                            </div>
                                        </Dropdown>
                                    {/each}
                                </Dropdown>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        {:else}
            <div class="mt-12 flex items-start gap-2.5">
                <div
                    class="flex flex-col w-full max-w-full leading-1.5 p-4 border-gray-200 bg-gray-50 rounded-l-xl rounded-b-xl dark:bg-gray-700 ml-4"
                >
                    <div
                        class="flex items-center space-x-2 rtl:space-x-reverse"
                    >
                        <span
                            class="text-sm font-semibold text-gray-900 dark:text-white"
                            >{per.sender}</span
                        >
                        <span
                            class="text-sm font-normal text-gray-500 dark:text-gray-400"
                            >{per.timestamp}</span
                        >
                    </div>
                    <p
                        class="text-sm font-normal py-2.5 text-gray-900 dark:text-white"
                    >
                        {per.message}
                    </p>
                </div>
                <img
                    class="w-8 h-8 rounded-full mr-4"
                    src={per.image}
                    alt="Jese image"
                />
            </div>
        {/if}
    {/each}

    {#if setuju}
        <div class="pt-8 max-w-full mx-4 mb-72">
            {#if loading}
                <div class="text-left"><Spinner /></div>
            {:else}
                <ButtonGroup class="w-full">
                    <Textarea
                        id="input-addon"
                        type="email"
                        placeholder="Isi Pertanyaaanmu"
                        class="w-full h-16"
                        bind:value={valInput}
                    />
                    <Button color="primary" on:click={() => inputMessage()}
                        >↩️ Kirim</Button
                    >
                </ButtonGroup>
            {/if}
        </div>
    {/if}
</div>
