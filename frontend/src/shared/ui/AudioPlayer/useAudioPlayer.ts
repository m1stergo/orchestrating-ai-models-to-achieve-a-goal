import { onUnmounted, ref } from 'vue'

const audioPlayer = ref<HTMLAudioElement | null>(null)
let killPrevious: (() => void) | null = null

export function useAudioPlayer() {
    const audio = ref<string | null>(null)
    const isPlaying = ref(false)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    
    const stop = () => {
        if (audioPlayer.value) {
            audioPlayer.value.pause()
            audioPlayer.value.currentTime = 0
            isPlaying.value = false
        }
    }

    function reset() {
        stop()
        isPlaying.value = false
        isLoading.value = false
        error.value = null
    }
    
    const play = async () => {
        if (!audio.value) {
            error.value = 'No audio URL provided'
            return
        }

        killPrevious?.();

        try {
            // Create new audio instance
            const newAudio = new Audio()
            
            // Set up event listeners before setting src
            newAudio.addEventListener('loadstart', () => {
                isLoading.value = true
            })
            
            newAudio.addEventListener('canplay', () => {
                isLoading.value = false
            })
            
            newAudio.addEventListener('ended', () => {
                isPlaying.value = false
                isLoading.value = false
            })
            
            newAudio.addEventListener('error', (e) => {
                isLoading.value = false
                isPlaying.value = false
                const audioError = newAudio.error
                if (audioError) {
                    switch (audioError.code) {
                        case MediaError.MEDIA_ERR_ABORTED:
                            error.value = 'Audio playback was aborted'
                            break
                        case MediaError.MEDIA_ERR_NETWORK:
                            error.value = 'Network error occurred while loading audio'
                            break
                        case MediaError.MEDIA_ERR_DECODE:
                            error.value = 'Audio format not supported or corrupted'
                            break
                        case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
                            error.value = 'Audio source not supported'
                            break
                        default:
                            error.value = 'Unknown audio error occurred'
                    }
                } else {
                    error.value = 'Failed to load audio'
                }
                console.error('Audio error:', error.value, e)
            })

            // Set the audio source
            newAudio.src = audio.value
            audioPlayer.value = newAudio
            
            // Load the audio
            newAudio.load()
            
            // Play the audio
            await newAudio.play()
            isPlaying.value = true
            isLoading.value = false
            killPrevious = reset
        } catch (e) {
            isLoading.value = false
            isPlaying.value = false
            error.value = e instanceof Error ? e.message : 'Failed to play audio'
            console.error('Audio play error:', e)
        }
    }

    onUnmounted(() => {
        reset()
    })

    return {
        audio,
        isPlaying,
        isLoading,
        error,
        play,
        stop,
    }
}