import { watch, ref } from "vue"
import { inference, warmup, type ServiceResponse, type DescribeImageInferenceParams, type DescribeImageWarmupParams } from "./api"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation, useQuery } from "@pinia/colada"

const isWarmingUp = ref(false)
const isLoading = ref(false)
const error = ref('')

export function useService(service: string, options?: { onSuccess?: (response: ServiceResponse<string>) => void, onError?: (error: Error) => void, }) {
    const { data: settings } = useQuery({
        key: ['settings'],
        query: () => getSettings(),
        refetchOnWindowFocus: false,
    })

    const { mutateAsync: triggerWarmup, isLoading: isLoadingWarmup } = useMutation({
        mutation: (params: DescribeImageWarmupParams) => warmup(service, params),
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        }
    })

    const { mutateAsync: inferenceMutation, isLoading: isLoadingInference } = useMutation({
        mutation: (params: DescribeImageInferenceParams) => inference(service, params),
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        },
        onSuccess: (data: ServiceResponse<string>) => {
            options?.onSuccess?.(data)
        }
    })

    async function run(params: { image_url: string, prompt?: string, model: string }) {
        await inferenceMutation(params)
    }

    watch(isLoadingWarmup, (value) => {
        isWarmingUp.value = value
    })

    watch(isLoadingInference, (value) => {
        isLoading.value = value
    })

    return {
        isWarmingUp,
        isLoading,
        run,
        error,
        settings,
        triggerWarmup,
    }
}
