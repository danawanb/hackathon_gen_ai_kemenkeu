<script>
    import {
        Dropzone,
        TabItem,
        Tabs,
        Textarea,
        Button,
        GradientButton,
        Spinner,
        Dropdown,
        DropdownItem,
        TableBodyRow,
        Table,
        TableHead,
        TableBody,
        Modal,
        Label,
        Input,
        TableBodyCell,
        TableHeadCell,
        Skeleton,
        Helper,
    } from "flowbite-svelte";
    import { onMount } from "svelte";
    import toast, { Toaster } from "svelte-french-toast";
    import {
        FilePptSolid,
        FileWordSolid,
        ChevronDownOutline,
        FileLinesSolid,
        ExclamationCircleOutline,
    } from "flowbite-svelte-icons";
    import axios from "axios";
    import { goto } from "$app/navigation";
    import {
        page_content_pdf,
        file_content_pdf,
        file_name,
        metadatas,
    } from "../../stores.js";
    import { DataHandler, Datatable } from "@vincjo/datatables";
    export let data;

    onMount(async () => {
        await get_data();
        console.log(data.slug);
    });
    let slugx = data.slug;
    let handler;
    let rows;
    let manual_type;
    let get_data = async () => {
        try {
            loading = true;
            let res = await axios.get(
                data.url + "/api/maker/get_data_from_header/" + data.slug,
                { withCredentials: true },
            );
            handler = new DataHandler(res.data, { rowsPerPage: 10 });
            rows = handler.getRows();
            loading = false;
        } catch (e) {
            loading = false;
            console.log(e);
            toast.error(e.toString());
        }
    };

    let value = [];
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

    let current_type = "pdf";

    let type_pdf = 1;

    let handle_insert = async (event) => {
        let insert_data = new FormData();

        switch (current_type) {
            case "pdf":
                switch (type_pdf) {
                    case 1:
                        try {
                            insert_data.append("file", filex[0]);
                            loading = true;

                            let res = await axios.post(
                                data.url + "/api/maker/store_pdf/1/" + slugx,
                                insert_data,
                                { withCredentials: true },
                            );

                            if (res.data.jmlh <= 5) {
                                //set draft string dan file pdfnya ke svelte store
                                page_content_pdf.set(res.data.page);
                                file_content_pdf.set(filex[0]);

                                file_name.set(res.data.file);

                                //await goto("/maker/draft_pdf/"+res2.data.file_name)
                                await goto("/maker/draft_pdf/" + slugx);
                            } else {
                                //store redis dan metadata ke vector db
                                let metad = {
                                    metadata: result_metada,
                                };
                                let res3 = await axios.post(
                                    data.url +
                                        "/api/maker/store_pdf_from_redis/" +
                                        res.data.idx +
                                        "/" +
                                        res.data.file +
                                        "/" +
                                        data.slug,
                                    metad,
                                    { withCredentials: true },
                                );
                                console.log(res3);

                                toast.success(
                                    "Berhasil Simpan Dokumen dan metadatanya",
                                );
                                await get_data();
                            }

                            loading = false;
                        } catch (err) {
                            console.log(err);
                            loading = false;
                            toast.error(err.toString());
                        }
                        break;
                    case 2:
                        try {
                            insert_data.append("file", filex[0]);
                            insert_data.append("judul", judul_aturan);
                            insert_data.append("nomor", no_aturan);

                            loading = true;

                            let res = await axios.post(
                                data.url + "/api/maker/store_pdf/2/" + slugx,
                                insert_data,
                                { withCredentials: true },
                            );

                            //tambahkan metadata mandatory
                            await handle_aturan_metadata("judul", judul_aturan);
                            await handle_aturan_metadata("nomor", no_aturan);

                            let metad = {
                                metadata: result_metada,
                            };
                            let res3 = await axios.post(
                                data.url +
                                    "/api/maker/store_pdf_id_cat_2/" +
                                    res.data.idx +
                                    "/" +
                                    res.data.file +
                                    "/" +
                                    data.slug,
                                metad,
                                { withCredentials: true },
                            );
                            console.log(res3);

                            toast.success(
                                "Berhasil Simpan Dokumen dan metadatanya",
                            );
                            setTimeout(() => {
                                window.location.reload();
                            }, 200);
                        } catch (err) {
                            console.log(err);
                            loading = false;
                            toast.error(err.toString());
                        }
                        break;
                }

                break;
            case "word":
                break;
            case "pptx":
                try {
                    console.log(filex[0].size);
                    if (filex[0].size >= 20000000) {
                        toast.error("Ukuran file terlalu besar");
                        return;
                    }

                    insert_data.append("file", filex[0]);
                    loading = true;

                    let res2 = await axios.post(
                        data.url + "/api/maker/upload_file",
                        insert_data,
                        { withCredentials: true },
                    );

                    let res = await axios.post(
                        data.url + "/api/maker/store_pptx",
                        insert_data,
                        { withCredentials: true },
                    );

                    if (res.data.jmlh <= 5) {
                        //set draft string dan file pdfnya ke svelte store
                        page_content_pdf.set(res.data.page);
                        file_content_pdf.set(filex[0]);
                        console.log(res2.data);
                        file_name.set(res2.data);

                        //await goto("/maker/draft_pdf/"+res2.data.file_name)
                        await goto("/maker/draft_pptx/" + slugx);
                    } else {
                        //store redis dan metadata ke vector db
                        let metad = {
                            metadata: result_metada,
                        };
                        let res3 = await axios.post(
                            data.url +
                                "/api/maker/store_pdf_from_redis/" +
                                res.data.idx +
                                "/" +
                                res2.data +
                                "/" +
                                data.slug,
                            metad,
                            { withCredentials: true },
                        );
                        console.log(res3);

                        toast.success(
                            "Berhasil Simpan Dokumen dan metadatanya",
                        );
                        await get_data();
                    }

                    loading = false;
                } catch (err) {
                    console.log(err);
                    loading = false;
                    toast.error(err.toString());
                }
                break;
            case "manual":
                try {
                    loading = true;
                    switch (manual_type) {
                        case "faq":
                            let faq_data = {
                                page_content:
                                    manual_pertanyaan + " ? " + manual_jawaban,
                                metadata: result_metada,
                                category_id: 4,
                            };
                            await axios.post(
                                data.url + "/api/maker/store_manual/" + slugx,
                                faq_data,
                                { withCredentials: true },
                            );
                            toast.success("Berhasil input FAQ");
                            loading = false;
                            await goto("/maker/success");
                            break;
                        case "penjelasan":
                            let manual_data = {
                                page_content: manual_jawaban,
                                metadata: result_metada,
                                category_id: 3,
                            };
                            await axios.post(
                                data.url + "/api/maker/store_manual/" + slugx,
                                manual_data,
                                { withCredentials: true },
                            );
                            toast.success("Berhasil input manual");
                            loading = false;
                            await goto("/maker/success");
                            break;
                        default:
                            loading = false;
                            toast.error("pilih jenis yang sesuai");
                    }
                } catch (e) {
                    loading = false;
                    console.log(e);
                }
            default:
                loading = false;
                console.log("tdk ada jenis file yg sesuai");
        }
    };
    let loading = false;
    let filex;
    let metada_modal = false;
    $: metadatax = [];

    let key;
    let valuex;

    let result_metada;
    let handle_add_metadata = async () => {
        let single_value = { key: key, val: valuex };
        metadatax = [...metadatax, single_value];
        key = "";
        valuex = "";
        metadatas.set(metadatax);

        result_metada = metadatax.reduce((acc, item) => {
            acc[item.key] = item.val;
            return acc;
        }, {});
        console.log(result_metada);
    };

    let handle_aturan_metadata = async (keyx, valx) => {
        let single_value = { key: keyx, val: valx };
        metadatax = [...metadatax, single_value];
        metadatas.set(metadatax);

        result_metada = metadatax.reduce((acc, item) => {
            acc[item.key] = item.val;
            return acc;
        }, {});
        console.log(result_metada);
    };

    //manual
    let manual_pertanyaan;
    let manual_jawaban;
    let delete_modal = false;

    let handle_delete = async () => {
        try {
            delete_loading = true;
            await axios.post(
                data.url +
                    "/api/maker/delete_knowledge/" +
                    current_ids +
                    "/" +
                    slugx,
                {},
                { withCredentials: true },
            );
            toast.success("berhasil hapus");
            delete_loading = false;
            delete_modal = false;
            await get_data();
        } catch (e) {
            delete_loading = false;
            console.log(e);
            toast.error(e.toString());
        }
    };

    let current_ids;

    let delete_loading = false;
    let no_aturan = "";
    let judul_aturan = "";

    let current_update_text = "";

    let update_modal = false;
    let update_loading = false;

    let handle_update_knowledge = async () => {
        try {
            update_loading = true;
            await axios.post(
                data.url +
                    "/api/maker/update_knowledge_list/" +
                    slugx +
                    "/" +
                    current_ids,
                {},
                { withCredentials: true },
            );
            toast.success("berhasil hapus");
            update_loading = false;
            update_modal = false;
            await get_data();
        } catch (e) {
            update_modal = false;
            console.log(e);
            toast.error(e.toString());
        }
    };

    let handle_delete_knowledge = async () => {
        try {
            if (hapus_input !== "saya yakin akan menghapus") {
                toast.error("kalimat inputan tidak sesuai");
                return;
            }

            await axios.post(
                data.url + "/api/maker/delete_header/" + slugx,
                {},
                { withCredentials: true },
            );

            delete_all_loading = true;
            toast.success("berhasil hapus");
            delete_all_loading = false;
            hapus_knowledge_modal = false;
            await goto("/maker/create");
        } catch (e) {
            hapus_knowledge_modal = false;
            console.log(e);
            toast.error(e.toString());
        }
    };

    let hapus_input = "";
    let hapus_knowledge_modal = false;
    let delete_all_loading = false;
</script>

<div class="mx-12 mt-8">
    <Toaster />
    <div class="mb-4">
        <Button
            on:click={() => {
                goto("/maker/create");
            }}
            class="mr-4">Kembali</Button
        >
        <Button
            on:click={() => (hapus_knowledge_modal = true)}
            color="red"
            class="border-red-600">⛔ Hapus Knowledge ini</Button
        >
    </div>
    <Modal
        title="Konfirmasi Hapus Seluruh Knowledge"
        bind:open={hapus_knowledge_modal}
    >
        <div class="mb-4">
            <Label for="error" color="red" class="block mb-2"
                >Ketikan : <p class="font-bold">
                    saya yakin akan menghapus
                </p></Label
            >
            <Input
                id="konfirmasi"
                bind:value={hapus_input}
                placeholder="Salin/Input kalimat di atas"
            />
        </div>
        <svelte:fragment slot="footer">
            <Button on:click={handle_delete_knowledge}>Yakin</Button>
            <Button
                color="alternative"
                on:click={() => (hapus_knowledge_modal = false)}>Tidak</Button
            >
        </svelte:fragment>
    </Modal>
    <Modal title="Add Metadata" bind:open={metada_modal} size="xl">
        <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
            Metadata didefinisikan sebagai data yang menyediakan informasi
            tentang satu atau lebih aspek data; digunakan untuk meringkas
            informasi dasar tentang data yang dapat mempermudah pelacakan dan
            pengerjaan data tertentu. Contoh metadata : judul : peraturan
            tentang bendahara, tahun : 2021, kategori : perpajakan, topik :
            pengelolaan kas, topik khusus : pengelolaan kas bendahara, tahun
            berlaku : 2024
        </p>
        <div class="">
            <div class="mb-4">
                <Label for="title" class="block mb-2">Name</Label>
                <Input id="title" placeholder="Name" bind:value={key} />
            </div>
            <div class="mb-4">
                <Label for="value" class="block mb-2">Value</Label>
                <Textarea
                    id="title"
                    placeholder="Value"
                    bind:value={valuex}
                    class="h-24"
                />
            </div>
        </div>
        <Button size="sm" on:click={handle_add_metadata}>Add</Button>
        <Table>
            <TableHead>
                <TableHeadCell>Key</TableHeadCell>
                <TableHeadCell>Value</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if metadatax}
                    {#each metadatax as meta}
                        <TableBodyRow>
                            <TableBodyCell>{meta.key}</TableBodyCell>
                            <TableBodyCell>{meta.val}</TableBodyCell>
                        </TableBodyRow>
                    {/each}
                {/if}
            </TableBody>
        </Table>
    </Modal>
    <div>
        <Tabs
            tabStyle="full"
            defaultClass="flex rounded-lg divide-x rtl:divide-x-reverse divide-gray-200 shadow dark:divide-gray-700"
        >
            <TabItem
                class="w-full"
                open
                on:click={() => {
                    value = [];
                    current_type = "pdf";
                }}
            >
                <span slot="title">📑 Upload PDF Document</span>
                <h4 class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    Tambahkan dokumen PDFmu di sini dengan maksimal ukuran file
                    adalah 20Mb. Pastikan menambahkan metadata agar dokumen
                    mudah diidentifikasi dan dikelompokkan
                </h4>
                <Tabs tabStyle="underline">
                    <TabItem
                        open
                        title="📚 Umum"
                        on:click={() => {
                            type_pdf = 1;
                        }}
                    >
                        <p
                            class="text-sm mb-2 text-gray-500 dark:text-gray-400"
                        >
                            <b
                                >Dokumen Selain Peraturan (Apabila kurang dari 5
                                Page akan masuk draft)</b
                            >
                        </p>

                        <Dropzone
                            accept=".pdf"
                            id="dropzone"
                            on:drop={dropHandle}
                            on:dragover={(event) => {
                                event.preventDefault();
                            }}
                            on:change={handleChange}
                            bind:files={filex}
                        >
                            <svg
                                aria-hidden="true"
                                class="mb-3 w-10 h-10 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                /></svg
                            >
                            {#if value.length === 0}
                                <p
                                    class="mb-2 text-sm text-gray-500 dark:text-gray-400"
                                >
                                    <span class="font-semibold"
                                        >Click to upload</span
                                    > or drag and drop
                                </p>
                                <p
                                    class="text-xs text-gray-500 dark:text-gray-400"
                                >
                                    PDF (MAX. 20 MB)
                                </p>
                            {:else}
                                <p>{showFiles(value)}</p>
                            {/if}
                        </Dropzone>
                    </TabItem>
                    <TabItem
                        title="📜 Peraturan"
                        on:click={() => {
                            type_pdf = 2;
                        }}
                    >
                        <p
                            class="text-sm mb-2 text-gray-500 dark:text-gray-400"
                        >
                            <b
                                >Dokumen Peraturan (PMK, Perdirjen, UU, Perpres,
                                dll)</b
                            >
                        </p>
                        <div class="flex flex-row">
                            <Textarea
                                label="Nomor"
                                id="text"
                                name="text"
                                class="bg-white h-12 mb-4 mr-4"
                                placeholder="Input Nomor Peraturan"
                                bind:value={no_aturan}
                            />
                            <Textarea
                                label="Judul"
                                id="text"
                                name="text"
                                class="bg-white h-12 mb-4"
                                placeholder="Input Judul Peraturan"
                                bind:value={judul_aturan}
                            />
                        </div>
                        <Dropzone
                            accept=".pdf"
                            id="dropzone"
                            on:drop={dropHandle}
                            on:dragover={(event) => {
                                event.preventDefault();
                            }}
                            on:change={handleChange}
                            bind:files={filex}
                        >
                            <svg
                                aria-hidden="true"
                                class="mb-3 w-10 h-10 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                /></svg
                            >
                            {#if value.length === 0}
                                <p
                                    class="mb-2 text-sm text-gray-500 dark:text-gray-400"
                                >
                                    <span class="font-semibold"
                                        >Click to upload</span
                                    > or drag and drop
                                </p>
                                <p
                                    class="text-xs text-gray-500 dark:text-gray-400"
                                >
                                    PDF (MAX. 20 MB)
                                </p>
                            {:else}
                                <p>{showFiles(value)}</p>
                            {/if}
                        </Dropzone>
                    </TabItem>
                </Tabs>
            </TabItem>
            <TabItem
                class="w-full"
                on:click={() => {
                    value = [];
                    current_type = "pptx";
                }}
            >
                <span slot="title">📕 Upload Powerpoint Document</span>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    Tambahkan dokumen PowerPointmu di sini dengan maksimal
                    ukuran file adalah 20Mb. Pastikan menambahkan metadata agar
                    dokumen mudah diidentifikasi dan dikelompokkan
                </p>
                <Dropzone
                    accept=".pptx"
                    id="dropzone"
                    on:drop={dropHandle}
                    on:dragover={(event) => {
                        event.preventDefault();
                    }}
                    bind:files={filex}
                    on:change={handleChange}
                >
                    <FilePptSolid class="mb-3 w-10 h-10 text-gray-400" />
                    {#if value.length === 0}
                        <p
                            class="mb-2 text-sm text-gray-500 dark:text-gray-400"
                        >
                            <span class="font-semibold">Klik untuk upload</span>
                            atau drag and drop
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">
                            PPTX (MAX. 20 MB)
                        </p>
                    {:else}
                        <p>{showFiles(value)}</p>
                    {/if}
                </Dropzone>
            </TabItem>
            <TabItem
                class="w-full"
                on:click={() => {
                    value = [];
                    current_type = "word";
                }}
            >
                <span slot="title">📘Upload Word Document</span>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                    <b>Settings:</b>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
                    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
                <Dropzone
                    accept=".pdf"
                    id="dropzone"
                    on:drop={dropHandle}
                    on:dragover={(event) => {
                        event.preventDefault();
                    }}
                    on:change={handleChange}
                >
                    <FileWordSolid class="mb-3 w-10 h-10 text-gray-400" />
                    {#if value.length === 0}
                        <p
                            class="mb-2 text-sm text-gray-500 dark:text-gray-400"
                        >
                            <span class="font-semibold">Klik untuk upload</span>
                            atau drag and drop
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">
                            PDF (MAX. 20 MB)
                        </p>
                    {:else}
                        <p>{showFiles(value)}</p>
                    {/if}
                </Dropzone>
            </TabItem>
            <TabItem
                class="w-full"
                on:click={() => {
                    value = [];
                    current_type = "manual";
                    manual_type = "penjelasan";
                }}
            >
                <span slot="title">📝 Manual</span>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    Tambahkan Knowledge secara manual
                </p>
                <Tabs tabStyle="underline">
                    <TabItem
                        open
                        title="📚 Penjelasan"
                        on:click={() => {
                            manual_type = "pejelasan";
                        }}
                    >
                        <p
                            class="text-sm mb-2 text-gray-500 dark:text-gray-400"
                        >
                            <b>Dokumen Manual</b>
                        </p>
                        <Textarea
                            class="h-[200px] bg-white"
                            bind:value={manual_jawaban}
                        />
                    </TabItem>
                    <TabItem
                        title="❓ Faq"
                        on:click={() => {
                            manual_type = "faq";
                        }}
                    >
                        <p
                            class="text-sm mb-2 text-gray-500 dark:text-gray-400"
                        >
                            <b>Tambahkan Pertanyaan dan Jawaban</b>
                        </p>
                        <Label class="block mb-2 text-gray-500"
                            >Pertanyaan</Label
                        >
                        <Input
                            label="Pertanyaan"
                            id="text"
                            name="text"
                            class="bg-white h-12 mb-4"
                            placeholder="Input pertanyaanmu"
                            bind:value={manual_pertanyaan}
                        />
                        <Label class="block mb-2 text-gray-500">Jawaban</Label>
                        <Textarea
                            class="h-[150px] bg-white"
                            bind:value={manual_jawaban}
                        />
                    </TabItem>
                </Tabs>
            </TabItem>
        </Tabs>
    </div>
    <div class="mt-12 mb-12">
        {#if loading}
            <GradientButton color="purpleToBlue" class="mr-4">
                <Spinner class="me-3" size="4" color="white" />Loading ...
            </GradientButton>
        {:else}
            <GradientButton
                color="purpleToBlue"
                class="mr-4"
                on:click={handle_insert}>Simpan</GradientButton
            >
        {/if}
        <Button
            on:click={() => (metada_modal = true)}
            color="alternative"
            class="border-blue-600 mr-4">➕ Add Metadata</Button
        >
    </div>
    <div>
        {#if handler}
            <Datatable
                {handler}
                class="border border-gray-150 rounded-lg px-2 py-2 mb-6"
            >
                <table class=" mt-4">
                    <thead class="display mt-4">
                        <tr>
                            <th class="w-4">No</th>
                            <th class="w-[70%]">Deskripsi</th>
                            <th class="w-2">File</th>
                            <th class="w-2">Action</th>
                        </tr>
                    </thead>
                    <tbody class="border-2">
                        {#each $rows as row, i}
                            <tr>
                                <td
                                    class="p-[4px] text-center border border-gray-150 hover:bg-gray-100"
                                    >{i + 1}</td
                                >
                                <td
                                    class="p-[4px] border border-gray-150 hover:bg-gray-100"
                                    ><p class="whitespace-pre-wrap">
                                        {row.page_content}
                                    </p></td
                                >
                                <td
                                    class="p-[4px] text-center border border-gray-150 hover:bg-gray-100"
                                >
                                    {#if row.file == "-"}
                                        <p>Tidak ada file</p>
                                    {:else}
                                        <Button
                                            on:click={() => {
                                                window.open(
                                                    data.url +
                                                        "/api/maker/get_file/" +
                                                        row.file,
                                                    "_blank",
                                                );
                                            }}><FileLinesSolid /> File</Button
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
                                    <Dropdown>
                                        <DropdownItem
                                            on:click={() => {
                                                update_modal = true;
                                                current_ids = row.ids;
                                                current_update_text =
                                                    row.page_content;
                                            }}>Update</DropdownItem
                                        >
                                        <DropdownItem
                                            on:click={() => {
                                                delete_modal = true;
                                                current_ids = row.ids;
                                            }}>Delete</DropdownItem
                                        >
                                    </Dropdown>
                                </td></tr
                            >
                        {/each}
                        <Modal bind:open={delete_modal} size="xs" autoclose>
                            <div class="text-center">
                                <ExclamationCircleOutline
                                    class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200"
                                />
                                <h3
                                    class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400"
                                >
                                    Apakah yakin akan menghapus ini ? {current_ids}
                                </h3>
                                {#if delete_loading}
                                    <Button>
                                        <Spinner
                                            class="me-3"
                                            size="4"
                                            color="white"
                                        />
                                        Loading ...
                                    </Button>
                                {:else}
                                    <Button
                                        color="red"
                                        class="me-2"
                                        on:click={handle_delete}>Ya</Button
                                    >
                                    <Button
                                        color="alternative"
                                        on:click={() => (delete_modal = false)}
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
                                bind:value={current_update_text}
                            ></Textarea>

                            <svelte:fragment slot="footer">
                                <Button on:click={handle_update_knowledge}
                                    >Simpan</Button
                                >
                                <Button
                                    color="alternative"
                                    on:click={() => (update_modal = false)}
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
    </div>
</div>
