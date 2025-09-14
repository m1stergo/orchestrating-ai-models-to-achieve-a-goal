import { watch, ref, reactive } from "vue"
import { inference, warmup, type ServiceResponse, type DescribeImageInferenceParams, type DescribeImageWarmupParams } from "./api"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation, useQuery } from "@pinia/colada"

const state = reactive<Record<string, any>>({})

export function useService(service: string, options?: { onSuccess?: (response: ServiceResponse<string>) => void, onError?: (error: Error) => void, }) {
    if (!state[service]) {
        state[service] = {
            isWarmingUp: false,
            isLoading: false,
            error: '',
        }
    }

    const { data: settings } = useQuery({
        key: ['settings'],
        query: () => getSettings(),
        refetchOnWindowFocus: false,
    })

    const { mutateAsync: triggerWarmup, isLoading: isLoadingWarmup } = useMutation({
        mutation: (params: DescribeImageWarmupParams) => warmup(service, params),
        onError: (err: Error) => {
            options?.onError?.(err)
            state[service].error = err.message
        }
    })

    const { mutateAsync: inferenceMutation, isLoading: isLoadingInference } = useMutation({
        mutation: (params: DescribeImageInferenceParams) => inference(service, params),
        onError: (err: Error) => {
            options?.onError?.(err)
            state[service].error = err.message
        },
        onSuccess: (data: ServiceResponse<string>) => {
            options?.onSuccess?.(data)
        }
    })

    async function run(params: { image_url: string, prompt?: string, model: string }) {
        await inferenceMutation(params)
    }

    watch(isLoadingWarmup, (value) => {
        state[service].isWarmingUp = value
    })

    watch(isLoadingInference, (value) => {
        state[service].isLoading = value
    })

    return {
        isWarmingUp: state[service].isWarmingUp,
        isLoading: state[service].isLoading,
        run,
        error: state[service].error,
        settings,
        triggerWarmup,
    }
}
