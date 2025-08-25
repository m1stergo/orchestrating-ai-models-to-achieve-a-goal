<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { useAudioPlayer } from './useAudioPlayer'
import Button from 'primevue/button'

const props = defineProps<{ audio: string, label?: string }>()
const { audio, isPlaying, isLoading, error, play, stop } = useAudioPlayer()

onMounted(() => {
    audio.value = props.audio
})

watch(() => props.audio, () => {
    if (isPlaying.value) stop()
    audio.value = props.audio
})
</script>

<template>
    <Button
        severity="help"
        variant="outlined"
        :rounded="label ? false : true"
        :size="label ? 'md' : 'small'"
        :loading="isLoading"
        :disabled="!audio || !!error"
        :icon="isPlaying ? 'pi pi-stop' : 'pi pi-play'"
        :title="error || (audio ? 'Play audio' : 'No audio available')"
        :label="label"
        @click="isPlaying ? stop() : play()" />
</template>
