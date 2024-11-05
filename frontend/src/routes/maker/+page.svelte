<script>
    import {
        Alert,
        Card,
        Toggle,
        Button,
        Label,
        Input,
        Modal,
    } from "flowbite-svelte";
    import { onMount } from "svelte";
    import { ArrowRightOutline } from "flowbite-svelte-icons";
    import { Bar } from "svelte-chartjs";
    import axios from "axios";
    import {
        Chart,
        Title,
        Tooltip,
        Legend,
        BarElement,
        CategoryScale,
        LinearScale,
    } from "chart.js";

    Chart.register(
        Title,
        Tooltip,
        Legend,
        BarElement,
        CategoryScale,
        LinearScale,
    );
    import { goto } from "$app/navigation";
    export let data;

    onMount(async () => {
        await get_data_dashboard();
    });

    let datax;
    $: datax;

    let get_data_dashboard = async () => {
        try {
            let resx = await axios.get(data.url + "/api/maker/dashboard", {
                withCredentials: true,
            });
            let item = resx.data.map((item) => item.title);
            console.log(item);
            let datax2 = {
                labels: resx.data.map((item) => item.title),
                datasets: [
                    {
                        label: "Pencarian paling populer",
                        data: resx.data.map((item) => item.countx),
                        backgroundColor: [
                            "#023e8a",
                            "#0077b6",
                            "#0096c7",
                            "#00b4d8",
                            "#48cae4",
                        ],
                    },
                ],
            };
            console.log(datax2);
            datax = datax2;
        } catch (e) {
            console.log(e);
        }
    };
</script>

<div class="mt-12 mx-12 flex flex-row gap-4">
    <div class="mr-4">
        <div class="mt-16 mb-8">
            <h2 class="text-4xl font-bold">Selamat Sore 💫🌇🌤</h2>
        </div>
        <p class="max-w-3xl text-xl font-semibold">
            Secara sederhana alur dan peran dalam TreasuryAI terbaik menjadi dua
            yakni maker dan user, maker memiliki peran untuk membuat knowledge
            base dan melakukan evalusi atas pertanyaan dan jawaban yang telah
            digenerate LLM sedangkan user dapat memiliki akses untuk bertanya
            dan mengetahui detail peraturan serta dokumen-dokumen lain
            berdasarkan pertanyaan yang telah diajukan
        </p>
        <Button
            class="mt-4"
            on:click={() => {
                goto("/chat");
            }}>Mulai Chat</Button
        >
    </div>
    <div class="space-y-4 mr-4">
        <Card
            class="max-w-lg"
            img="https://api.tinycode.cloud/api/maker/image/4bef7b7f-7300-494d-9d9c-d950fa7a7b0a.webp"
        >
            <h5
                class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
            >
                Create 👩🏻‍💻📓✍🏻💡
            </h5>
            <p
                class="mb-3 font-normal text-gray-700 dark:text-gray-400 leading-tight"
            >
                Digunakan untuk merekam knowledge/pengetahuan yang akan disimpan
                dan dijadikan konteks untuk chat, generate soal, generate
                peraturan, generate frequently asked question (FAQ) yang dapat
                diakses oleh pengguna. Tersedia juga fitur untuk melakukan hapus
                atau edit knowledge/pengetahuan
            </p>
            <Button on:click={() => goto("/maker/create")}>
                Rekam Knowledge<ArrowRightOutline
                    class="w-6 h-6 ms-2 text-white"
                />
            </Button>
        </Card>
    </div>
    <div class="space-y-4 mr-4">
        <Card
            class="max-w-lg"
            img="https://turso.tech/_next/image?url=%2Fimages%2Fblog%2Fastro-chooses-turso-to-power-astro-db%2Fcover.png&w=3840&q=100"
        >
            <h5
                class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
            >
                Evaluate 🔎📊⚖️🤔
            </h5>
            <p
                class="mb-3 font-normal text-gray-700 dark:text-gray-400 leading-tight"
            >
                Digunakan untuk melihat analis trend berdasarkan pertanyaan yang
                diajukan oleh pengguna serta digunakan untuk melakukan evaluasi
                secara otomatis/manual atas pertanyaan dan jawaban yang diajukan
                oleh pengguna. Dapat pula digunakan untuk merubah soal dan
                jawaban yang telah digenerate otomatis berdasarkan konteks yang
                ada
            </p>
            <Button
                on:click={() => {
                    goto("/eval");
                }}
            >
                Evaluate Knowledge<ArrowRightOutline
                    class="w-6 h-6 ms-2 text-white"
                />
            </Button>
        </Card>
    </div>
</div>
<hr class="my-12 h-0.5 border-t-0 bg-neutral-100 dark:bg-white/10" />
<div class="mt-8 max-w-2xl max-h-xl mx-12 flex flex-row">
    {#if datax}
        <Bar data={datax} options={{ responsive: true }} />
        <Bar data={datax} options={{ responsive: true }} />
    {:else}
        <p>Gaa ada</p>
    {/if}
</div>
