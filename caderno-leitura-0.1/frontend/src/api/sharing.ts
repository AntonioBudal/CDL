import { api } from '../services/api.ts'
import type {
  Book,
  BookVisibility,
  ResourcePermissionItem,
  ResourcePermissionsRead,
  ResourceVisibility,
  SharedBooksResponse,
  SharedStudiesResponse,
} from '../types.ts'

export const sharingApi = {
  getStudyPermissions: (studyId: number, signal?: AbortSignal): Promise<ResourcePermissionsRead> =>
    api.getStudyPermissions(studyId, signal),

  updateStudyVisibility: (
    studyId: number,
    visibility: ResourceVisibility,
  ): Promise<ResourcePermissionsRead> =>
    api.updateStudyVisibility(studyId, visibility),

  updateBookVisibility: (
    bookId: number,
    visibility: BookVisibility,
  ): Promise<Book> =>
    api.updateBookVisibility(bookId, visibility),

  grantStudyPermission: (
    studyId: number,
    username: string,
  ): Promise<ResourcePermissionItem> =>
    api.grantStudyPermission(studyId, username),

  revokeStudyPermission: (
    studyId: number,
    userId: string,
  ): Promise<{ ok: boolean }> =>
    api.revokeStudyPermission(studyId, userId),

  getSharedStudies: (
    params?: { q?: string; author?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ): Promise<SharedStudiesResponse> =>
    api.getSharedStudies(params, signal),

  getSharedBooks: (
    params?: { q?: string; limit?: number; offset?: number },
    signal?: AbortSignal,
  ): Promise<SharedBooksResponse> =>
    api.getSharedBooks(params, signal),
}

export default sharingApi
