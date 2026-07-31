import AuthShell from "@/components/auth/AuthShell";
import ForgotPasswordForm from "@/components/auth/ForgotPasswordForm";

export default function ForgotPasswordPage() {
  return (
    <AuthShell
      eyebrow="Account recovery"
      title="Reset your password"
      description="Enter your email and we will help you get back to your favorite stories."
      footer={<>Remember your password? <a href="/login" className="font-medium text-white transition-colors hover:text-[#ff5962]">Sign in</a></>}
    >
      <ForgotPasswordForm />
    </AuthShell>
  );
}
