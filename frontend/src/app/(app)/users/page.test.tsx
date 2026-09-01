import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import UsersPage from "./page";

const apiFetch = vi.fn();
vi.mock("@/lib/api/client", () => ({
  apiFetch: (...args: unknown[]) => apiFetch(...args),
  ApiError: class extends Error {},
  queryString: () => "",
}));
vi.mock("@/components/auth/manager-route", () => ({ ManagerRoute: ({ children }: { children: React.ReactNode }) => children }));
vi.mock("@/lib/hooks/use-api-query", () => ({ useApiQuery: () => ({ loading: false, error: null, reload: vi.fn(), data: { items: [], page: 1, pages: 0, total: 0 } }) }));

describe("user form", () => {
  it("shows the production password requirements before submitting", async () => {
    render(<UsersPage />);
    await userEvent.click(screen.getByRole("button", { name: "Add user" }));
    await userEvent.type(screen.getByLabelText("Full name"), "Chad Example");
    await userEvent.type(screen.getByLabelText("Email"), "chad@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "short123");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText(passwordError)).toBeVisible();
    expect(apiFetch).not.toHaveBeenCalled();
  });
});

const passwordError = "Use at least 12 characters with uppercase, lowercase, and a number";
