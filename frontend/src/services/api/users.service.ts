import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type { UserProfile } from "@/types/auth";

import { apiClient } from "./client";

export const usersService = {
  async getMe(): Promise<UserProfile> {
    const { data } = await apiClient.get<ApiResponse<UserProfile>>("/users/me");
    assertApiSuccess(data);
    return data.data;
  },
};
