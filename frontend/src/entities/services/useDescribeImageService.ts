import { watch, ref } from "vue"
import { describeImageInference, describeImageStatus, describeImageWarmup } from "./api"
import { useQuery } from "@pinia/colada"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation } from "@pinia/colada"
import { poll } from "./poll"

const isWarmingUp = ref(false)
const isLoading = ref(false)
const error = ref('')
const action = ref('')

export function useDescribeImageService(options?: { onSuccess?: (response: any) => void, onError?: (error: Error) => void }) {
    const { data: settings } = useQuery({
        key: ['settings'],
        query: () => getSettings(),
        refetchOnWindowFocus: false,
    })
    
    const { mutateAsync: triggerDescribeImageStatus } = useMutation({
        mutation: describeImageStatus,
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        },
        onSuccess: (data) => {
            if (data.status === "COMPLETED" && data.details?.status === "IDLE") {
                if (isLoading.value) {
                    options?.onSuccess?.(data.details?.data)
                }
                isLoading.value = false
                isWarmingUp.value = false

            }
            if (data.details?.status === "PROCESSING") {
                isLoading.value = true
            }
            if (data.details?.status === "WARMINGUP") {
                isWarmingUp.value = true
            }
            if (data.details?.status === "ERROR") {
                isWarmingUp.value = false
                isLoading.value = false
                error.value = data.details?.message
            }
        },  
    })

    const { mutateAsync: triggerDescribeImageWarmup } = useMutation({
        mutation: describeImageWarmup,
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        }
    })

    const { mutateAsync: describeImageMutation } = useMutation({
        mutation: describeImageInference,
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        }
    })

    watch(settings, async(newSettings, oldSettings) => {
        if (newSettings?.describe_image_model !== oldSettings?.describe_image_model) {
            const { id } = await triggerDescribeImageWarmup({ model: newSettings?.describe_image_model! })
            checkStatus(id, newSettings?.describe_image_model!)
        }
    })

    async function checkStatus(id: string, model: string) {
        try {
            await poll(() => triggerDescribeImageStatus({ model, job_id: id }));
        } catch (err: any) {
            options?.onError?.(err)
            error.value = err.message
        }
    }

    async function describeImage(params: { image_url: string, prompt?: string, model: string }) {
        const { id } = await describeImageMutation(params)
        checkStatus(id, params.model)
    }

    return {
        isWarmingUp,
        isLoading,
        describeImage,
        error
    }
}
