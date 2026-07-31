import AuthShell from "@/components/auth/AuthShell";
import RegisterForm from "@/components/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <AuthShell
      eyebrow="Start your journey"
      title="Create your account"
      description="Build your personal library and make every night a movie night."
      footer={<>Already have an account? <a href="/login" className="font-medium text-white transition-colors hover:text-[#ff5962]">Sign in</a></>}
    >
      <RegisterForm />
    </AuthShell>
  );
}
