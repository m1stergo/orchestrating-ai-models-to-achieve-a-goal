import { watch, computed } from "vue"
import { describeImageInference, describeImageStatus, describeImageWarmup } from "./api"
import { useQuery } from "@pinia/colada"
import { getSettings } from "@/features/UserSettings/api"
import { useMutation } from "@pinia/colada"
import { checkStatus } from "./checkStatus"

export function useDescribeImageService(options?: { onSuccess?: () => void, onError?: (error: Error) => void }) {
    const { data: settings } = useQuery({
        key: ['settings'],
        query: () => getSettings(),
        refetchOnWindowFocus: false,
    })
    
    const { mutateAsync: triggerDescribeImageStatus, isLoading: isLoadingDescribeImageStatus } = useMutation({
        mutation: describeImageStatus,
        onError: options?.onError
    })

    const { mutateAsync: triggerDescribeImageWarmup, isLoading: isLoadingDescribeImageWarmup } = useMutation({
        mutation: describeImageWarmup,
        onError: options?.onError
    })


    const { data: describeImageData, mutateAsync: describeImage, isLoading: isLoadingDescribeImageInference } = useMutation({
        mutation: describeImageInference,
        onSuccess: options?.onSuccess,
        onError: options?.onError
    })

    watch(settings, async(newSettings, oldSettings) => {
        if (newSettings?.describe_image_model !== oldSettings?.describe_image_model) {
            const { id } = await triggerDescribeImageWarmup({ model: newSettings?.describe_image_model! })
            try {
                await checkStatus(() => triggerDescribeImageStatus({ model: newSettings?.describe_image_model!, job_id: id }));
            } catch (error) {
                options?.onError?.(error as Error)
            }
        }
    })

    return {
        describeImageData,
        isWarmingUp: isLoadingDescribeImageWarmup,
        isLoading: computed(() => isLoadingDescribeImageInference.value || isLoadingDescribeImageStatus.value || isLoadingDescribeImageWarmup.value),
        describeImage
    }
}
