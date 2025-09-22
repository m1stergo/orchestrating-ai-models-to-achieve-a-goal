<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useQuery } from '@pinia/colada'
import { getAvailableVoices } from './api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'
import Textarea from 'primevue/textarea'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { AudioPlayer } from '@/shared/ui/AudioPlayer'
import { useProductForm } from '@/composables/useProductForm'
import { useService } from '@/entities/services/useService'

const props = defineProps<{ model?: string, prompt?: string }>()

const form = useProductForm()

const toast = useToast()

const selectedVoice = ref<any>(null)

const dirty = ref(false);

const audioDescription = computed({
    get: () => form.values.audio_description,
    set: (value) => {
        form.setFieldValue('audio_description', value)
        dirty.value = true
    }
})

const { data: voices } = useQuery({
  key: ['voices'],
  query: () => getAvailableVoices(),
})

const generateDescription = useService('generate-description/promotional-audio-script', {
    onSuccess: (response: any) => {
        const parsedData = parseDescriptionResponse(response.data)
        form.setFieldValue('audio_description', parsedData.description)
        dirty.value = false
    },
    onError: () => {
        toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the promotional audio script, please try again', life: 3000 });
    },
})

const tts = useService('text-to-speech', {
    onSuccess: (response: any) => {
      form.setFieldValue('audio', response.data)
    },
    onError: (error) => {
      console.error('TTS generation error:', error)
      toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the audio, please try again', life: 3000 });
    },
})

async function generateSpeech() {
    try {
        await generateDescription.run({
            text: form?.values.description,
            prompt: props.prompt,
            model: props.model,
        })
    } catch (error) {
        console.error('Error generating promotional audio script:', error)
    }
}

async function generateAudio() {
    if (!form?.values.audio_description) {
        toast.add({ severity: 'warn', summary: 'Warning', detail: 'Please ensure the promotional script is not empty', life: 3000 });
        return
    }

    try {
        await tts.run({
            text: form?.values.audio_description,
            model: 'chatterbox',
            voice_url: selectedVoice.value.audio_url
        })
    } catch (error) {
        console.error('Error generating promotional audio:', error)
    }
}


function parseDescriptionResponse(data: string) {
  try {
    // Try to parse as JSON
    const parsed = JSON.parse(data)
    
    // Validate that it has the expected structure
    if (typeof parsed === 'object' && parsed !== null) {
      return {
        description: parsed.description,
      }
    }
  } catch (error) {
    console.warn('Failed to parse description as JSON:', error)
  }
  
  // Fallback: return original description with empty other fields
  return {
    description: data,
  }
}

onMounted(() => {
  tts.warmup({ model: 'chatterbox' })
})

watch(voices, (newVoices) => {
  if (newVoices.length > 0 && !selectedVoice.value) {
    selectedVoice.value = newVoices[0]
  }
})
</script>

<template>
    <div class="flex flex-col gap-4 mb-6">
        <Button 
            :disabled="generateDescription.isLoadingInference.value"
            :loading="generateDescription.isLoadingInference.value"
            :label="generateDescription.isLoadingInference.value ? 'Generating promotional audio script...' : 'Generate promotional audio script'"     
            :severity="form?.values.audio_description ? 'primary' : 'help'"
            variant="outlined"
            @click="generateSpeech" />
        <div v-if="generateDescription.isLoadingInference.value">
            <Skeleton height="5rem" />
        </div>
        <div v-else-if="form?.values.audio_description || dirty" class="space-y-2">
            <Textarea
                class="w-full border border-gray-300 rounded-md p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                v-model="audioDescription"
                autoResize />
        </div>

        <div v-if="form?.values.audio_description">
            <label class="text-sm font-medium text-gray-700 mb-2">Select a voice actor:</label>
            <div class="space-y-2">
                <div
                    v-for="voice in voices || []"
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
        <Message v-if="tts.error.value" severity="error" class="flex justify-center">
            <div class="flex items-center gap-2 justify-center text-center">
               Text to speech model is not available, please try again later. {{ tts.error.value }}
            </div>
        </Message>
        <Message v-else-if="!tts.isReady.value" severity="warn" class="flex justify-center">
            <div class="flex items-center gap-2 justify-center text-center">
                <ProgressSpinner class="w-6 h-6" />
                Text to speech model is warming up, please wait a few seconds...
            </div>
        </Message> 
        <Button 
            v-else-if="form?.values.audio_description"
            :disabled="tts.isLoadingInference.value"
            :label="tts.isLoadingInference.value ? 'Generating audio... this may take a few seconds' : 'Generate promotional audio'"
            :loading="tts.isLoadingInference.value"
            :severity="form?.values.audio ? 'primary' : 'help'"
            variant="outlined"
            @click="generateAudio" />  
        <Skeleton v-if="tts.isLoadingInference.value" height="3rem" />
        <AudioPlayer v-if="form?.values.audio && !tts.isLoadingInference.value" :audio="form?.values.audio" label="Play generated audio" />
    </div>
</template>
