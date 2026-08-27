import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "./page";
const login=vi.fn();
vi.mock("@/components/auth/auth-provider",()=>({useAuth:()=>({login,user:null,loading:false})}));
describe("login",()=>{
 beforeEach(()=>login.mockReset());
 it("validates required credentials",async()=>{render(<LoginPage/>);fireEvent.click(screen.getByRole("button",{name:"Sign in"}));expect(await screen.findByText("Enter your email address")).toBeVisible();expect(screen.getByText("Enter your password")).toBeVisible()});
 it("submits valid credentials",async()=>{login.mockResolvedValue({});render(<LoginPage/>);await userEvent.type(screen.getByLabelText("Email"),"manager@example.com");await userEvent.type(screen.getByLabelText("Password"),"secret123");await userEvent.click(screen.getByRole("button",{name:"Sign in"}));await waitFor(()=>expect(login).toHaveBeenCalledWith("manager@example.com","secret123"))});
});
