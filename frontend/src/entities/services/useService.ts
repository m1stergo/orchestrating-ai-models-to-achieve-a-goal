import { computed, reactive, watch } from "vue"
import { inference, warmup, type ServiceResponse } from "./api"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation, useQuery } from "@pinia/colada"

// Define valid service names as a type
type ServiceName = 'describe-image' | 'generate-description' | 'text-to-speech' | 'generate-description/promotional-audio-script'

interface ServiceState {
    isLoadingWarmup: boolean;
    isLoadingInference: boolean;
    error: string;
}

const state = reactive<Record<ServiceName, ServiceState>>({ 
    'describe-image': {
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
    },
    'generate-description': {
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
    },
    'text-to-speech': { 
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
    },
    'generate-description/promotional-audio-script': { 
        isLoadingWarmup: false,
        isLoadingInference: false,
        error: '',
    },
})

export function useService(service: ServiceName, options?: { onSuccess?: (response: ServiceResponse<string>) => void, onError?: (error: Error) => void, }) {
    const { data: settings } = useQuery({
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
            }
        },
        onError: () => {
            state[service].isLoadingWarmup = false
            state[service].error = errorWarmup.value?.message || ''
        }
    })

    const { mutateAsync: inferenceMutateAsync, isLoading: isLoadingInference, error: errorInference } = useMutation({
        mutation: (params: Record<string, any>) => inference(service, params),
        onSuccess: (response: ServiceResponse<string>) => {
            options?.onSuccess?.(response)
            state[service].isLoadingInference = false
            state[service].error = ''
            if (response.status === 'FAILED') {
                state[service].error = response.message
            }
        },
        onError: (error: Error) => {
            options?.onError?.(error)
            state[service].isLoadingInference = false
            state[service].error = errorInference.value?.message || ''
        }
    })

    async function run(params: Record<string, any>) {
        await inferenceMutateAsync(params)
    }

    watch(() => isLoadingWarmup.value, () => {
        state[service].isLoadingWarmup = isLoadingWarmup.value
    })
    
    watch(() => isLoadingInference.value, () => {
        state[service].isLoadingInference = isLoadingInference.value
    })
    
    return {
        isLoadingWarmup: computed(() => state[service].isLoadingWarmup),
        isLoadingInference: computed(() => state[service].isLoadingInference),
        error: computed(() => state[service].error),
        run,
        warmup: triggerWarmup,
        settings,
    }
}
