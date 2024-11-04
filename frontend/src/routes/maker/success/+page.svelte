<script>
    import { Alert, Button } from "flowbite-svelte";
    import { InfoCircleSolid } from "flowbite-svelte-icons";
    import { goto } from "$app/navigation";
</script>

<div class="ml-[10%] mr-[10%] mt-36 mb-72">
    <Alert color="green">
        <div class="flex items-center gap-3">
            <InfoCircleSolid slot="icon" class="w-4 h-4" />
            <span class="text-lg font-medium">Berhasil Simpan</span>
        </div>
        <p class="mt-2 mb-4 text-sm">Draft anda sudah tersimpan 😎👌🔥</p>
        <Button
            on:click={() => {
                goto("/maker");
            }}>Kembali</Button
        >
    </Alert>
</div>
