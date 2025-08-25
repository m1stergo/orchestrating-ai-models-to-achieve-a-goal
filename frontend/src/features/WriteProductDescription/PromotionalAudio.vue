<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Product } from '@/entities/products'
import { useMutation, useQuery } from '@pinia/colada'
import { getAvailableVoices, generatePromotionalAudioScript, generateTextToSpeech } from './api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'
import Textarea from 'primevue/textarea'
import { AudioPlayer } from '@/shared/ui/AudioPlayer'

const props = defineProps<{ model?: string }>()

const product = defineModel<Product>({required: true})

const toast = useToast()

// Voice selection and reel/audio generation
const selectedVoice = ref<any>(null)

const dirty = ref(false);

const audioDescription = computed({
    get: () => product.value.audio_description,
    set: (value) => {
        product.value.audio_description = value
        dirty.value = true
    }
})

// Fetch available voices
const { data: voices } = useQuery({
  key: ['voices'],
  query: () => getAvailableVoices(),
})

// Reel generation mutation
const { mutateAsync: triggerGeneratePromotionalAudioScript, isLoading: isLoadingGeneratePromotionalAudioScript } = useMutation({
  mutation: () => generatePromotionalAudioScript({ text: product.value.description, model: props.model!}),
  onSuccess: (data) => {
    product.value.audio_description = data.text
    dirty.value = false
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the reel script, please try again', life: 3000 });
  },
})

// Text-to-speech generation mutation
const { mutateAsync: triggerGenerateAudio, isLoading: isLoadingGenerateAudio } = useMutation({
  mutation: generateTextToSpeech,
  onSuccess: (data) => {
    product.value.audio = data.audio_url
  },
  onError: (error) => {
    console.error('TTS generation error:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the audio, please try again', life: 3000 });
  },
})


async function generatePromotionalAudio() {
    if (!product.value.audio_description) {
        toast.add({ severity: 'warn', summary: 'Warning', detail: 'Please ensure the promotional script is not empty', life: 3000 });
        return
    }

    try {
        // Generate the audio using the reel script
        await triggerGenerateAudio({
            text: product.value.audio_description,
            model: 'chatterbox',
            audio_prompt_url: selectedVoice.value.audio_url
        })
    } catch (error) {
        console.error('Error generating promotional audio:', error)
    }
}

// Set first voice as default when voices are loaded
watch(voices, (newVoices) => {
  if (newVoices?.voices && newVoices.voices.length > 0 && !selectedVoice.value) {
    selectedVoice.value = newVoices.voices[0]
  }
})
</script>

<template>
    <div class="flex flex-col gap-4 mb-6">
        <Button 
            :disabled="isLoadingGeneratePromotionalAudioScript"
            :loading="isLoadingGeneratePromotionalAudioScript"
            :label="isLoadingGeneratePromotionalAudioScript ? 'Generating promotional audio script...' : 'Generate promotional audio script'"     
            :severity="product.audio_description ? 'primary' : 'help'"
            variant="outlined"
            @click="() => triggerGeneratePromotionalAudioScript()" />
        <div v-if="isLoadingGeneratePromotionalAudioScript">
            <Skeleton height="5rem" />
        </div>
        <div v-else-if="product.audio_description || dirty" class="space-y-2">
            <Textarea
                class="w-full border border-gray-300 rounded-md p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                v-model="audioDescription"
            ></Textarea>
        </div>

        <div v-if="product.audio_description">
            <label class="text-sm font-medium text-gray-700 mb-2">Select a voice actor:</label>
            <div class="space-y-2">
                <div
                    v-for="voice in voices?.voices || []"
                    :key="voice.name"
                    :class="[
                        'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-sm',
                        selectedVoice?.name === voice.name
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                    ]"
                    @click="selectedVoice = voice">
                    <AudioPlayer :audio="voice.audio_url" />
                    <span :class="[
                        'font-medium flex-1',
                        selectedVoice?.name === voice.name ? 'text-primary-700' : 'text-gray-700'
                    ]">
                        {{ voice.name }}
                    </span>
                </div>
            </div>
        </div>
        <Button 
            v-if="product.audio_description"
            :disabled="isLoadingGenerateAudio"
            :label="isLoadingGenerateAudio ? 'Generating audio... this may take a few seconds' : 'Generate promotional audio'"
            :loading="isLoadingGenerateAudio"
            :severity="product.audio ? 'primary' : 'help'"
            variant="outlined"
            @click="generatePromotionalAudio" />  
        <Skeleton v-if="isLoadingGenerateAudio" height="3rem" />
        <AudioPlayer v-if="product.audio && !isLoadingGenerateAudio" :audio="product.audio" label="Play generated audio" />
    </div>
</template>
