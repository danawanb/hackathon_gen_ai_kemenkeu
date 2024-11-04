<script>
    import {
        page_content_pdf,
        file_content_pdf,
        file_name,
        metadatas,
    } from "../../stores.js";
    import { onMount } from "svelte";
    import { Button, Textarea, Toggle } from "flowbite-svelte";
    import { goto } from "$app/navigation";
    import { Toaster, toast } from "svelte-french-toast";
    import axios from "axios";

    let page_content = [];
    let loading = false;
    let file_content;
    export let data;

    let metadatax = {};
    let filex;

    onMount(() => {
        try {
            page_content_pdf.subscribe((value) => {
                console.log(value);
                page_content = value.map((item) => {
                    return { ...item, checked: false };
                });
            });

            file_content_pdf.subscribe((value) => {
                file_content = value;
            });

            file_name.subscribe((value) => {
                filex = value;
            });

            metadatas.subscribe((value) => {
                metadatax = value;
            });
            console.log(data.slug);
        } catch (e) {
            console.log(e);
        }
    });

    let handle_simpan = async () => {
        loading = true;
        for (let i = 0; i < page_content.length; i++) {
            if (page_content[i].checked === false) {
                toast.error("Masih terdapat checklist yang belum sesuai");
                return;
            }
        }

        try {
            console.log(file_content);

            const new_page_content = page_content.map((item) => {
                return {
                    page_content: item.page_content,
                    metadata: metadatax[0],
                    checked: item.checked,
                    file: filex,
                    category_id: 2, // Menambahkan category_id dengan nilai 2
                };
            });
            console.log(metadatax);
            let datafile = new FormData();
            datafile.append("file", file_content);

            try {
                let res = await axios.post(
                    data.url + `/api/maker/store_list_from_draft/${data.slug}`,
                    new_page_content,
                    { withCredentials: true },
                );
                console.log(res);
                toast.success("Berhasil Simpan");
                goto("/maker/success");
            } catch (e) {
                console.log(e);
                toast.error(e.toString());
            }

            toast.success("Berhasil Simpan");
        } catch (e) {
            toast.error(e.toString());
        }
    };

    let key;
    let slugx = data.slug;
</script>

<div class="mx-12">
    <Toaster />
    <div class="my-6">
        <Button
            on:click={() => {
                goto("/maker/create/" + slugx);
            }}
            color="red"
            class="mr-4">❌ Reject</Button
        >
        <Button on:click={handle_simpan} class="mr-4">✅ Publish</Button>
    </div>
    <div class="mt-4">
        {#if page_content}
            {#each page_content as p}
                <div class="my-8">
                    <Textarea bind:value={p.page_content} class="h-[400px]"
                    ></Textarea>
                    <Toggle
                        class="mt-2"
                        checked={p.checked}
                        on:click={() => (p.checked = !p.checked)}>Sesuai</Toggle
                    >
                </div>
            {/each}
        {/if}
    </div>
</div>
