import { watch, ref } from "vue"
import { describeImageInference, describeImageStatus, describeImageWarmup } from "./api"
import { useQuery } from "@pinia/colada"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation } from "@pinia/colada"
import { checkStatus } from "./checkStatus"

const isWarmingUp = ref(false)
const isLoading = ref(false)
const error = ref('')

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
            if (data.details?.status === "IN_PROGRESS") {
                isLoading.value = true
            }
            if (data.status === "COMPLETED") {
                isLoading.value = false
            }
            if (data.details?.status === "LOADING") {
                isWarmingUp.value = true
            }
            if (data.details?.status === "IDLE") {
                isWarmingUp.value = false
            }
            if (data.details?.status === "ERROR") {
                isWarmingUp.value = false
                error.value = data.details?.message
            }
        },  
    })

    const { mutateAsync: triggerDescribeImageWarmup, reset } = useMutation({
        mutation: describeImageWarmup,
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        }
    })

    const { mutateAsync: describeImage } = useMutation({
        mutation: describeImageInference,
        onSuccess: options?.onSuccess,
        onError: (err: Error) => {
            options?.onError?.(err)
            error.value = err.message
        }
    })

    watch(settings, async(newSettings, oldSettings) => {
        if (newSettings?.describe_image_model !== oldSettings?.describe_image_model) {
            const { id } = await triggerDescribeImageWarmup({ model: newSettings?.describe_image_model! })
            try {
                await checkStatus(() => triggerDescribeImageStatus({ model: newSettings?.describe_image_model!, job_id: id }));
            } catch (err: any) {
                options?.onError?.(err)
                error.value = err.message
            }
        }
    })

    return {
        isWarmingUp,
        isLoading,
        describeImage,
        error
    }
}
