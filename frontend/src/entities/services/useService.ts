import { computed, ref, watch } from "vue";
import { describeImageWarmup, generateDescriptionWarmup, describeImageHealthCheck, generateDescriptionHealthCheck } from "./api";
import { useMutation } from '@pinia/colada'

const services = ref({
    generateDescription: {
        isSuccess: false,
        isLoading: false,
        retryCount: 0,
        error: false,
        isWarmingUp: false
    },
    describeImage: {
        isSuccess: false,
        isLoading: false,
        retryCount: 0,
        error: false,
        isWarmingUp: false
    }
})

let generateDescriptionHealthCheckInterval: any = null
let describeImageHealthCheckInterval: any = null

type ServiceName = keyof typeof services.value;

export function useService(serviceName: ServiceName) {
    const isLoading = computed(() => services.value[serviceName].isLoading)
    const error = computed(() => services.value[serviceName].error)
    const isSuccess = computed(() => services.value[serviceName].isSuccess)
    const model = ref<string>('')
    
    const MAX_RETRIES = 10

    const { mutateAsync: triggerDescribeImageWarmup } = useMutation({
        mutation: describeImageWarmup,
    })

    const { mutateAsync: triggerGenerateDescriptionWarmup } = useMutation({
        mutation: generateDescriptionWarmup,
    })

    const { mutateAsync: triggerDescribeImageHealthCheck } = useMutation({
        mutation: describeImageHealthCheck,
        onSuccess: (result) => {
            const status = result.status
            
            if (status === 'healthy') {
                services.value[serviceName].isSuccess = true
                services.value[serviceName].isLoading = false
                services.value[serviceName].retryCount = 0
                services.value[serviceName].error = false
                clearInterval(describeImageHealthCheckInterval)
            } else if (status === 'error' || status === 'unhealthy') {
                // Service is not healthy - trigger warmup on first retry
                services.value[serviceName].isSuccess = false
                
                if (services.value[serviceName].retryCount < 1) {
                    triggerDescribeImageWarmup(model.value)
                }
                
                services.value[serviceName].retryCount++
                
                if (services.value[serviceName].retryCount >= MAX_RETRIES) {
                    services.value[serviceName].error = true
                    services.value[serviceName].isLoading = false
                    clearInterval(describeImageHealthCheckInterval)
                }
            } else if (result.status === 'loading') {
                // Service is loading/warming up - keep checking
                services.value[serviceName].isSuccess = false
                // Don't increment retry count for loading status
            }
        },
        onError: () => {
            // This handles actual network errors, not HTTP 503 responses
            services.value[serviceName].retryCount++
            
            if (services.value[serviceName].retryCount >= MAX_RETRIES) {
                services.value[serviceName].error = true
                services.value[serviceName].isLoading = false
                clearInterval(describeImageHealthCheckInterval)
            }
        }
    })

    const { mutateAsync: triggerGenerateDescriptionHealthCheck } = useMutation({
        mutation: generateDescriptionHealthCheck,
        onSuccess: (result) => {
            const status = result.status
            
            if (status === 'healthy') {
                services.value[serviceName].isSuccess = true
                services.value[serviceName].isLoading = false
                services.value[serviceName].retryCount = 0
                services.value[serviceName].error = false
                clearInterval(generateDescriptionHealthCheckInterval)
            } else if (status === 'error' || status === 'unhealthy') {
                // Service is not healthy - trigger warmup on first retry
                services.value[serviceName].isSuccess = false
                
                if (services.value[serviceName].retryCount < 1) {
                    triggerGenerateDescriptionWarmup(model.value)
                }
                
                services.value[serviceName].retryCount++
                
                if (services.value[serviceName].retryCount >= MAX_RETRIES) {
                    services.value[serviceName].error = true
                    services.value[serviceName].isLoading = false
                    clearInterval(generateDescriptionHealthCheckInterval)
                }
            } else if (result.status === 'loading') {
                // Service is loading/warming up - keep checking
                services.value[serviceName].isSuccess = false
                // Don't increment retry count for loading status
            }
        },
        onError: () => {
            // This handles actual network errors, not HTTP 503 responses
            services.value[serviceName].retryCount++
            
            if (services.value[serviceName].retryCount >= MAX_RETRIES) {
                services.value[serviceName].error = true
                services.value[serviceName].isLoading = false
                clearInterval(generateDescriptionHealthCheckInterval)
            }
        }
    })

    function healthCheckGenerateDescription(model: string ) {
        if (generateDescriptionHealthCheckInterval) {
           return
        }

        // Execute immediately first time (like do-while)
        const executeHealthCheck = () => {
            console.log('healthCheck', 'generateDescription')
            triggerGenerateDescriptionHealthCheck(model)
        }
        
        // Then set interval for subsequent checks
        generateDescriptionHealthCheckInterval = setInterval(executeHealthCheck, 10000)

        // Execute immediately
        return executeHealthCheck()
    }

    function healthCheckDescribeImage(model: string) {
        if (describeImageHealthCheckInterval) {
            return
        }

        // Execute immediately first time (like do-while)
        const executeHealthCheck = () => {
            console.log('healthCheck', 'describeImage')
            triggerDescribeImageHealthCheck(model)
        }
        
        // Then set interval for subsequent checks
        describeImageHealthCheckInterval = setInterval(executeHealthCheck, 10000)

        // Execute immediately
        return executeHealthCheck()
    }

    watch(model, async (newValue) => {
        if (!newValue) return
        if (serviceName === 'describeImage') {
            services.value['describeImage'].isLoading = true
            services.value['describeImage'].error = false
            services.value['describeImage'].isSuccess = false
            services.value['describeImage'].retryCount = 0
            services.value['describeImage'].isWarmingUp = false
            healthCheckDescribeImage(model.value)
        }
        if (serviceName === 'generateDescription') {
            services.value['generateDescription'].isLoading = true
            services.value['generateDescription'].error = false
            services.value['generateDescription'].isSuccess = false
            services.value['generateDescription'].retryCount = 0
            services.value['generateDescription'].isWarmingUp = false
            healthCheckGenerateDescription(model.value)
        }
    })

    return {
        isLoading,
        error,
        isSuccess,
        model,
    }
}