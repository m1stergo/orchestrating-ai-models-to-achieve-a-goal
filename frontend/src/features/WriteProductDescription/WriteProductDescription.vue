<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import UploadImage from './UploadImage.vue'
import type { ExtractWebContentResponse } from './types'
import { useMutation, useQuery } from '@pinia/colada'
import { describeImage, generateDescription, extractWebContent, getAvailableVoices, generateReelScript, generateTextToSpeech } from './api'
import { useToast } from 'primevue/usetoast'
import { getSettings } from '../UserSettings/api'
import Stepper from 'primevue/stepper'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import ProgressSpinner from 'primevue/progressspinner'
import Skeleton from 'primevue/skeleton'

// Content source selection
const contentSourceOptions = [
  { name: 'Extract from website', value: 'website' },
  { name: 'Upload image', value: 'image' }
]
const selectedContentSource = ref(contentSourceOptions[0])

const toast = useToast()

const source = reactive<ExtractWebContentResponse>({
    title: '',
    description: '',
    images: [],
    url: '',
})

// Obtener las configuraciones del usuario
const { data: settings } = useQuery({
  key: ['settings'],
  query: () => getSettings(),
})

const uploadedImage = ref('')

const status = ref({
    isLoadingExtractWebContent: true,
    isLoadingDescribeImage: true,
    isLoadingGenerateDescription: true,
    isLoadingGenerateReel: false,
    isLoadingGenerateAudio: false,
})
  
const { data: extractWebContentData, mutateAsync: triggerExtractWebContent } = useMutation({
  mutation: extractWebContent,
  onSuccess: (data) => {
    status.value.isLoadingExtractWebContent = false
    source.images = data.images
    source.url = data.url
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error extracting the content, please try again', life: 3000 })
  },
})

const { data: imageDescriptionData, mutateAsync: triggerDescribeImage } = useMutation({
  mutation: describeImage,
  onSuccess: () => {
    status.value.isLoadingDescribeImage = false
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error describing the image, please try again', life: 3000 });
  },
})

const { mutateAsync: triggerGenerateDescription } = useMutation({
  mutation: generateDescription,
  onSuccess: (data) => {
    status.value.isLoadingGenerateDescription = false
    source.description = data.description
  },
  onError: () => {
    toast.add({ severity: 'error', summary: 'Rejected', detail: 'There was an error generating the description, please try again', life: 3000 });
  },
})

const beginProcessEnabled = computed(() => {
  if (selectedContentSource.value.value === 'website') {
    return source.url !== ''
  }
  if (selectedContentSource.value.value === 'image') {
    return uploadedImage.value !== ''
  }
  return false
})

const activeStep = ref(1)
const generateDescriptionEnabled = ref(false)

// Voice selection and reel/audio generation  
const selectedVoice = ref<any>(null)
const reelScript = ref('')
const audioUrl = ref('')
const lastProcessedDescription = ref('')

// Audio playback management
const currentPlayingAudio = ref<HTMLAudioElement | null>(null)
const currentPlayingVoice = ref<string | null>(null)

// Fetch available voices
const { data: voices } = useQuery({
  key: ['voices'],
  query: () => getAvailableVoices(),
})

// Set first voice as default when voices are loaded
watch(voices, (newVoices) => {
  if (newVoices?.voices && newVoices.voices.length > 0 && !selectedVoice.value) {
    selectedVoice.value = newVoices.voices[0]
  }
})

// Auto-generate reel script when entering audio step or when description changes
watch([activeStep, () => source.description], ([newStep, newDescription]) => {
  if (newStep === 3 && newDescription) {
    // Generate script if it's empty or description has changed
    if (!reelScript.value || lastProcessedDescription.value !== newDescription) {
      autoGenerateReelScript()
    }
  }
})

// Reel generation mutation
const { mutateAsync: triggerGenerateReel } = useMutation({
  mutation: generateReelScript,
  onSuccess: (data) => {
    status.value.isLoadingGenerateReel = false
    reelScript.value = data.text
  },
  onError: () => {
    status.value.isLoadingGenerateReel = false
    toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the reel script, please try again', life: 3000 });
  },
})

// Text-to-speech generation mutation
const { mutateAsync: triggerGenerateAudio } = useMutation({
  mutation: generateTextToSpeech,
  onSuccess: (data) => {
    status.value.isLoadingGenerateAudio = false
    console.log('TTS generation success, received data:', data)
    console.log('Setting audioUrl to:', data.audio_url)
    audioUrl.value = data.audio_url
  },
  onError: (error) => {
    status.value.isLoadingGenerateAudio = false
    console.error('TTS generation error:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'There was an error generating the audio, please try again', life: 3000 });
  },
})


async function beginProcess() {
    status.value.isLoadingExtractWebContent = true
    status.value.isLoadingDescribeImage = true
    status.value.isLoadingGenerateDescription = true
    generateDescriptionEnabled.value = true
    activeStep.value = 2
    source.title = ''
    source.description = ''

    if (selectedContentSource.value.value === 'website') {
        if (!source.url) return
        await triggerExtractWebContent(source.url)
    }

    if (!source.images.length) return
    await triggerDescribeImage({
        image_url: source.images[0],
        model: (settings.value as any)?.describe_image_model || ''
    })

    if (!imageDescriptionData.value?.description) return
    await triggerGenerateDescription({
        text: extractWebContentData.value?.title + ' ' + imageDescriptionData.value?.description,
        model: (settings.value as any)?.generate_description_model || 'openai'
    })
}

const toggleVoicePlayback = (audioUrl: string, event: Event) => {
    event.stopPropagation()
    
    // If this audio is currently playing, pause it
    if (currentPlayingVoice.value === audioUrl) {
        if (currentPlayingAudio.value) {
            currentPlayingAudio.value.pause()
            currentPlayingAudio.value = null
            currentPlayingVoice.value = null
        }
        return
    }
    
    // Stop any currently playing audio
    if (currentPlayingAudio.value) {
        currentPlayingAudio.value.pause()
        currentPlayingAudio.value = null
        currentPlayingVoice.value = null
    }
    
    // Start playing the new audio
    const audio = new Audio(audioUrl)
    currentPlayingAudio.value = audio
    currentPlayingVoice.value = audioUrl
    
    audio.addEventListener('ended', () => {
        currentPlayingAudio.value = null
        currentPlayingVoice.value = null
    })
    
    audio.play().catch(error => {
        console.error('Error playing audio sample:', error)
        currentPlayingAudio.value = null
        currentPlayingVoice.value = null
        toast.add({ 
            severity: 'error', 
            summary: 'Error', 
            detail: 'Could not play voice sample', 
            life: 3000 
        })
    })
}

const playGeneratedAudio = (e: Event) => {
    e.stopPropagation()
    if (audioUrl.value) {
        toggleVoicePlayback(audioUrl.value, e)
    } else {
        toast.add({ 
            severity: 'warn', 
            summary: 'Warning', 
            detail: 'No audio URL available to play', 
            life: 3000 
        })
    }
}

const autoGenerateReelScript = async () => {
    if (!source.description) return
    
    status.value.isLoadingGenerateReel = true
    try {
        await triggerGenerateReel({
            text: source.description,
            model: (settings.value as any)?.generate_description_model || 'openai'
        })
        lastProcessedDescription.value = source.description
    } catch (error) {
        console.error('Error generating reel script:', error)
    }
}

const updateReelScript = (event: Event) => {
    const target = event.target as HTMLDivElement
    reelScript.value = target.innerText
}

async function generatePromotionalAudio() {
    if (!selectedVoice.value || !reelScript.value) {
        toast.add({ severity: 'warn', summary: 'Warning', detail: 'Please select a voice and ensure the promotional script is ready', life: 3000 });
        return
    }

    status.value.isLoadingGenerateAudio = true

    try {
        // Generate the audio using the reel script
        await triggerGenerateAudio({
            text: reelScript.value,
            model: 'chatterbox',
            audio_prompt_url: selectedVoice.value.audio_url
        })
    } catch (error) {
        status.value.isLoadingGenerateAudio = false
        console.error('Error generating promotional audio:', error)
    }
}

watch(uploadedImage, () => {
    if (uploadedImage.value) {
        source.images = [uploadedImage.value]
    }
})
</script>

<template>
    <div class="card">
        <Stepper v-model:value="activeStep">
            <StepItem :value="1">
                <Step>Select content source</Step>
                <StepPanel>
                    <div class="flex flex-col gap-4">
                        <Select id="contentSource"
                            v-model="selectedContentSource"
                            :options="contentSourceOptions"
                            optionLabel="name"
                            placeholder="Select a content source"
                            class="w-full" />
                        <InputText v-if="selectedContentSource.value === 'website'" v-model="source.url" placeholder="Enter a URL" />
                        <UploadImage v-if="selectedContentSource.value === 'image'" v-model="uploadedImage" />
                    </div>
                    <div class="py-6">
                        <Button :disabled="!beginProcessEnabled" label="Generate description" @click="beginProcess" />
                    </div>
                </StepPanel>
            </StepItem>
            <StepItem :value="2">
                <Step :disabled="!generateDescriptionEnabled">Product description</Step>
                <StepPanel>
                    <div v-if="selectedContentSource.value === 'website'" class="flex items-center gap-2">
                        <ProgressSpinner v-if="status.isLoadingExtractWebContent" strokeWidth="4" style="width: 25px; height: 25px" />
                        <i v-else class="pi pi-check" />
                        <p class="text-sm w-full">Extracting content...</p>
                    </div>
                    <!-- Analyzing image skeleton -->
                    <div v-if="status.isLoadingDescribeImage">
                        <div class="flex flex-col gap-2">
                            <p class="text-sm text-gray-600 mb-2">Analyzing image...</p>
                            <div class="flex gap-2">
                                <Skeleton size="5rem" v-for="i in 3" :key="i"></Skeleton>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Show image after analysis, then description generation -->
                    <div v-else class="flex flex-col gap-2">
                        <!-- Show the image -->
                        <div class="flex gap-2">
                            <div v-if="source.images.length > 0">
                                <div v-for="image in source.images" :key="image">
                                    <img :src="image" alt="Image" class="w-24 rounded">
                                </div>
                            </div>
                            <div v-else>
                                <img :src="uploadedImage" alt="Uploaded Image" class="w-24 rounded">
                            </div>
                        </div>
                        
                        <!-- Show description generation skeleton or final description -->
                        <div v-if="status.isLoadingGenerateDescription">
                            <div class="flex flex-col gap-2">
                                <p class="text-sm text-gray-600 mb-2">Generating product description...</p>
                                <Skeleton height="2rem"></Skeleton>
                                <Skeleton height="4rem"></Skeleton>
                            </div>
                        </div>
                        <div v-else>
                            <div v-html="source.description" contenteditable="true" />
                            <div class="py-6">
                                <Button label="Generate promotional audio" @click="activeStep = 3" />
                            </div>
                        </div>
                    </div>
                </StepPanel>
            </StepItem>
            <StepItem :value="3">
                <Step :disabled="!generateDescriptionEnabled">Promotional audio</Step>
                <StepPanel>
                    <div class="flex flex-col gap-4 mb-6">
                        <!-- Generated Reel Script -->
                        <div>
                            <div v-if="status.isLoadingGenerateReel">
                              <p class="text-sm text-gray-600 mb-2">Generating promotional script...</p>
                                <Skeleton height="2rem"></Skeleton>
                            </div>
                            <div v-else-if="reelScript" class="space-y-2">
                                <p class="text-sm text-gray-600">Edit the script below if needed:</p>
                                <div 
                                    contenteditable="true"
                                    @input="updateReelScript"
                                    class="border border-gray-300 rounded-md p-3 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    v-html="reelScript"
                                ></div>
                            </div>
                            <div v-else class="text-gray-500 italic">
                                Script will be generated automatically when you enter this step.
                            </div>
                        </div>

                        <!-- Voice Selection -->
                        <div v-if="reelScript && !status.isLoadingGenerateReel">
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
                                  <Button 
                                      :icon="currentPlayingVoice === voice.audio_url ? 'pi pi-pause' : 'pi pi-play'" 
                                      :severity="currentPlayingVoice === voice.audio_url ? 'success' : 'secondary'" 
                                      rounded
                                      size="small"
                                      @click="toggleVoicePlayback(voice.audio_url, $event)" />
                                  <span :class="[
                                      'font-medium flex-1',
                                      selectedVoice?.name === voice.name ? 'text-primary-700' : 'text-gray-700'
                                  ]">
                                      {{ voice.name }}
                                  </span>
                              </div>
                          </div>
                        </div>
                    </div>
                    
                    <div class="flex gap-4">
                      <div v-if="reelScript && !status.isLoadingGenerateReel">
                          <Button 
                              :disabled="status.isLoadingGenerateReel || status.isLoadingGenerateAudio"
                              :loading="status.isLoadingGenerateReel || status.isLoadingGenerateAudio"
                              label="Generate promotional audio" 
                          @click="generatePromotionalAudio" />
                      </div>
                    
                      <!-- Play Generated Audio Button - only show when audioUrl exists -->
                      <div v-if="audioUrl">
                          <Button 
                              :icon="currentPlayingVoice === audioUrl ? 'pi pi-pause' : 'pi pi-play'"
                              severity="success"
                              :label="currentPlayingVoice === audioUrl ? 'Pause Generated Audio' : 'Play Generated Audio'"
                              @click="playGeneratedAudio" />
                      </div>
                    </div>
                </StepPanel>
            </StepItem>
        </Stepper>
    </div>
</template>
