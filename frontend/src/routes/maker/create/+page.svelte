<script>
    import {
        Card,
        Button,
        Toggle,
        Modal,
        Input,
        Label,
        Fileupload,
        Dropzone,
        Textarea,
        Spinner,
        CardPlaceholder,
    } from "flowbite-svelte";
    import {
        ArrowRightOutline,
        SearchSolid,
        AngleLeftOutline,
        FileWordSolid,
        FileImageSolid,
    } from "flowbite-svelte-icons";
    import { goto } from "$app/navigation";
    import { toast, Toaster } from "svelte-french-toast";
    import Select from "svelte-select";
    import axios from "axios";
    import { onMount } from "svelte";
    export let data;
    let add_modal = false;
    let title = "";
    onMount(async () => {
        await get_data_header();
    });
    let value = [];
    let filex;
    const dropHandle = (event) => {
        value = [];
        filex = [];
        event.preventDefault();
        if (event.dataTransfer.items) {
            [...event.dataTransfer.items].forEach((item, i) => {
                if (item.kind === "file") {
                    const file = item.getAsFile();
                    value.push(file.name);
                    value = value;
                    filex.push(file);
                }
            });
        } else {
            [...event.dataTransfer.files].forEach((file, i) => {
                value = file.name;
                filex.push(file);
            });
        }
    };

    //handle perubahan nama dropzone
    const handleChange = (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            value = [files[0].name];
        } else if (files.length > 1) {
            toast.error("Maksimal file yang diupload 1");
        }
    };

    //menampikan nama file jika banyak
    const showFiles = (files) => {
        if (files.length === 1) return files[0];
        let concat = "";
        files.map((file) => {
            concat += file;
            concat += ",";
            concat += " ";
        });

        if (concat.length > 40) concat = concat.slice(0, 40);
        concat += "...";
        return concat;
    };

    let selected_cat;
    let categories = [
        { value: 1, label: "Umum" },
        { value: 2, label: "Peraturan" },
    ];

    let add_topics = async () => {
        try {
            loading = true;
            let insert_val = new FormData();
            if (filex) {
                insert_val.append("title", title);
                insert_val.append("category_id", selected_cat.value);
                insert_val.append("image", filex[0]);
            } else {
                insert_val.append("title", title);
                insert_val.append("category_id", selected_cat.value);
            }
            let res = await axios.post(
                data.url + "/api/maker/create_header",
                insert_val,
                { withCredentials: true },
            );
            console.log(res.data);
            toast.success("berhasil");
            loading = false;
            await goto("/maker/create/" + res.data.ids_header);
        } catch (e) {
            console.log(e);
            loading = false;
            toast.error(e.toString());
        }
    };

    // http://localhost:8000/api/maker/image/8cc26a96-7580-4cfd-b327-80acdaf1f278.webp
    let loading = false;
    let datax = [];

    let err = false;
    let get_data_header = async () => {
        try {
            let res = await axios.get(data.url + "/api/maker/get_all_header", {
                withCredentials: true,
            });
            datax = res.data.data.map((item) => {
                return {
                    ids: item.ids,
                    title: item.title,
                    image_url: data.url + "/api/maker/image/" + item.image_url,
                };
            });
            searching = false;
        } catch (e) {
            console.log(e);
            err = true;
            toast.error(e.toString());
        }
    };
    let timeout;

    let handle_search = () => {
        searching = true;
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(fetch_data, 300);
    };

    let fetch_data = async () => {
        if (!search) {
            reset();
            await get_data_header();
            return;
        }

        try {
            let res = await axios.get(
                data.url + "/api/maker/get_all_header?search=" + search,
                { withCredentials: true },
            );
            datax = res.data.data.map((item) => {
                return {
                    ids: item.ids,
                    title: item.title,
                    image_url: data.url + "/api/maker/image/" + item.image_url,
                };
            });
            searching = false;
        } catch (e) {
            err = true;
            console.log(e);
            handle_error();
        }
    };

    let reset = () => {
        datax = [];
        searching = false;
    };
    let search;
    let searching = false;

    let handle_error = () => {
        toast.error("Data Tidak ditemukan");
        reset();
    };

    //deleted variable search dan fetch lagi
    let delete_search = async () => {
        search = "";
        await fetch_data();
    };

    let handle_goto = (ids) => {
        goto("/maker/create/" + ids);
    };
</script>

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
    <Button
        on:click={() => {
            add_modal = true;
        }}>➕ Tambah</Button
    >
</div>
<div class="mx-12 mt-4 mb-4">
    <Input
        id="search"
        type="text"
        bind:value={search}
        on:input={handle_search}
        placeholder="search topics"
    >
        <SearchSolid
            slot="left"
            class="w-5 h-5 text-gray-500 dark:text-gray-400"
        />
    </Input>
</div>
<Modal title="Add Topics" bind:open={add_modal} size="xl">
    <div class="mb-4">
        <Label for="title" class="block mb-2">Judul</Label>
        <Textarea
            id="title"
            placeholder="Judul"
            bind:value={title}
            class="h-24"
        />
    </div>
    <div class="mb-4">
        <Label for="title" class="block mb-2">Kategori</Label>
        <Select
            class="mt-2"
            items={categories}
            bind:value={selected_cat}
            placeholder="Pilih kategori"
        />
    </div>
    <div class="mb-6">
        <Dropzone
            accept="image/*"
            id="dropzone"
            on:drop={dropHandle}
            on:dragover={(event) => {
                event.preventDefault();
            }}
            on:change={handleChange}
            bind:files={filex}
        >
            <FileImageSolid class="mb-3 w-10 h-10 text-gray-400" />
            {#if value.length === 0}
                <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span class="font-semibold">Klik untuk upload</span> atau drag
                    and drop
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                    Image (MAX. 4 MB)
                </p>
            {:else}
                <p>{showFiles(value)}</p>
            {/if}
        </Dropzone>
    </div>
    <svelte:fragment slot="footer">
        {#if loading}
            <Button class="border-blue-600">
                <Spinner class="me-3" size="4" color="white" />Loading ...
            </Button>
        {:else}
            <Button class="border-blue-600" on:click={add_topics}>Simpan</Button
            >
        {/if}
        <Button
            color="alternative"
            on:click={() => {
                add_modal = false;
            }}>Batal</Button
        >
    </svelte:fragment>
</Modal>
<div class="mx-12 mt-12 grid grid-cols-4 gap-4">
    {#if err}
        <p>Terjadi error saat ambil data</p>
    {/if}
    {#if searching}
        <CardPlaceholder />
        <CardPlaceholder />
        <CardPlaceholder />
        <CardPlaceholder />
    {:else if datax}
        {#each datax as dat}
            <div>
                <Card img={dat.image_url} class="max-h-45">
                    <h5
                        class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white"
                    >
                        {dat.title}
                    </h5>
                    <Button
                        color="alternative"
                        class="border-blue-600"
                        on:click={() => handle_goto(dat.ids)}
                    >
                        Details <ArrowRightOutline
                            class="w-6 h-6 ms-2 text-blue-600"
                        />
                    </Button>
                </Card>
            </div>
        {/each}
    {/if}
</div>
