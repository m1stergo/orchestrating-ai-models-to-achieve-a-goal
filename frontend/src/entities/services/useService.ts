import { computed, reactive, ref, watch } from "vue"
import { inference, warmup, type ServiceResponse } from "./api"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation, useQuery } from "@pinia/colada"

// Define valid service names as a type
type ServiceName = 'describe-image' | 'generate-description' | 'text-to-speech' | 'generate-description/audio-promo'

interface ServiceState {
    isLoadingWarmup: boolean;
    isLoadingInference: boolean;
    error: string;
    isReady: boolean;
}

const state = reactive<Record<ServiceName, ServiceState>>({ 
    'describe-image': {
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
        isReady: false,
    },
    'generate-description': {
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
        isReady: false,
    },
    'text-to-speech': { 
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
        isReady: false,
    },
    'generate-description/audio-promo': { 
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
        isReady: false,
    },
})

export function useService(service: ServiceName, options?: { onSuccess?: (response: ServiceResponse<string>) => void, onError?: (error: Error) => void, }) {
    const { data: settings, isLoading: isLoadingSettings } = useQuery({
        key: ['settings'],
        query: () => getSettings(),
        refetchOnWindowFocus: false,
    })

    const { mutateAsync: triggerWarmup, isLoading: isLoadingWarmup, error: errorWarmup } = useMutation({
        mutation: (params: Record<string, any>) => warmup(service, params),
        onSuccess: (response: ServiceResponse<string>) => {
            state[service].isLoadingWarmup = false
            state[service].error = ''
            if (response.status === 'FAILED') {
                state[service].error = response.message
                options?.onError?.(new Error(response.message))
            }
        },
        onError: () => {
            state[service].isLoadingWarmup = false
            state[service].error = errorWarmup.value?.message || ''
            options?.onError?.(new Error(state[service].error))
        }
    })

    const { mutateAsync: inferenceMutateAsync, isLoading: isLoadingInference, error: errorInference } = useMutation({
        mutation: (params: Record<string, any>) => inference(service, params),
        onSuccess: (response: ServiceResponse<string>) => {
            options?.onSuccess?.(response)
            state[service].isLoadingWarmup = false
            state[service].isLoadingInference = false
            state[service].error = ''
            if (response.status === 'FAILED') {
                state[service].error = response.message
                options?.onError?.(new Error(response.message))
            }
        },
        onError: (error: Error) => {
            options?.onError?.(error)
            state[service].isLoadingInference = false
            state[service].isLoadingWarmup = false
            state[service].error = errorInference.value?.message || ''
            options?.onError?.(new Error(state[service].error))
        }
    })

    watch(() => isLoadingWarmup.value, () => {
        state[service].isLoadingWarmup = isLoadingWarmup.value
        if (!isLoadingWarmup.value) {
            state[service].isReady = true
        }
    })
    
    watch(() => isLoadingInference.value, () => {
        state[service].isLoadingInference = isLoadingInference.value
    })
    
    return {
        isLoadingSettings,
        isLoadingWarmup: computed(() => state[service].isLoadingWarmup),
        isLoadingInference: computed(() => state[service].isLoadingInference),
        error: computed(() => state[service].error),
        run: (params: Record<string, any>) => { 
            const key = service === 'generate-description/audio-promo' ? 'generate-description' : service
            if (!state[key].isReady || state[key].isLoadingInference) return Promise.resolve({
                status: 'IN_PROGRESS',
                message: 'Service is not ready or is already running'
            })
            return inferenceMutateAsync(params)
        },
        warmup: (params: Record<string, any>) => { 
            triggerWarmup(params); 
        },
        settings,
        isReady: computed(() => {
            const key = service === 'generate-description/audio-promo' ? 'generate-description' : service
            return state[key].isReady
        }),
        dispose: () => {
            state[service].isReady = false
            state[service].isLoadingWarmup = false
            state[service].isLoadingInference = false
            state[service].error = ''
        }
    }
}
