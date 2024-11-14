<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-xl mx-auto bg-white rounded-lg shadow-md">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-2xl font-bold text-center flex items-center justify-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" 
               stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          YouTube Video Downloader
        </h1>
      </div>

      <!-- Main Content -->
      <div class="p-6">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- URL Input -->
          <div class="relative">
            <div class="flex gap-2">
              <div class="relative flex-1">
                <svg xmlns="http://www.w3.org/2000/svg" 
                     class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor" 
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                </svg>
                <input 
                  v-model="url"
                  type="text"
                  placeholder="Paste YouTube URL here..."
                  class="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:border-blue-500"
                  :class="{ 'border-red-500': error }"
                />
              </div>
              <button 
                type="submit"
                :disabled="isLoading"
                class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
              >
                {{ isLoading ? 'Processing...' : 'Download' }}
              </button>
            </div>
            <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
          </div>

          <!-- Video Info -->
          <div v-if="videoInfo" class="mt-4 p-4 bg-gray-50 rounded-md">
            <h3 class="font-medium text-lg mb-2">{{ videoInfo.title }}</h3>
            <div class="space-y-2">
              <p class="text-sm text-gray-600">Duration: {{ formatDuration(videoInfo.duration) }}</p>
              <div class="space-y-2">
                <p class="font-medium">Available Formats:</p>
                <div class="space-y-1">
                  <button
                    v-for="format in videoInfo.formats"
                    :key="format.format_id"
                    @click="downloadFormat(format.format_id)"
                    class="block w-full text-left px-3 py-2 text-sm bg-white border rounded hover:bg-gray-50"
                  >
                    {{ format.format_note }} - {{ format.ext }}
                    <span v-if="format.filesize" class="text-gray-500">
                      ({{ formatFileSize(format.filesize) }})
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="font-medium mb-2">How to use:</h3>
            <ol class="list-decimal ml-4 space-y-1 text-sm text-gray-600">
              <li>Copy the YouTube video URL you want to download</li>
              <li>Paste the URL in the input field above</li>
              <li>Click the Download button</li>
              <li>Choose your preferred format and quality</li>
              <li>Wait for the download to complete</li>
            </ol>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const url = ref('')
const error = ref('')
const isLoading = ref(false)
const videoInfo = ref(null)

const validateYouTubeUrl = (url) => {
  const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/
  return pattern.test(url)
}

const formatDuration = (seconds) => {
  if (!seconds) return 'Unknown'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown size'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

const handleSubmit = async () => {
  error.value = ''
  
  if (!url.value) {
    error.value = 'Please enter a YouTube URL'
    return
  }

  if (!validateYouTubeUrl(url.value)) {
    error.value = 'Please enter a valid YouTube URL'
    return
  }

  try {
    isLoading.value = true
    const response = await fetch('http://localhost:8000/api/video-info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url.value })
    })

    if (!response.ok) {
      throw new Error('Failed to fetch video information')
    }

    videoInfo.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

const downloadFormat = async (formatId) => {
  try {
    isLoading.value = true
    const response = await fetch('http://localhost:8000/api/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url.value,
        format: formatId
      })
    })

    if (!response.ok) {
      throw new Error('Download failed')
    }

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${videoInfo.value.title || 'video'}.mp4`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(downloadUrl)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}
</script>