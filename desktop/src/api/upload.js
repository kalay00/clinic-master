import { upload as uploadFile, del } from '@/utils/request'

export function uploadImage(file, data = {}) {
  return uploadFile('/upload/image', file, data).then(res => res.data)
}

export function deleteImage(url) {
  return del(`/upload/image?url=${encodeURIComponent(url)}`).then(res => res.data)
}

export default {
  uploadImage,
  deleteImage
}
