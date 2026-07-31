import AuthShell from "@/components/auth/AuthShell";
import LoginForm from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <AuthShell
      eyebrow="Welcome back"
      title="Sign in to StreamSphere"
      description="Pick up where you left off and discover something worth watching."
      footer={<>New to StreamSphere? <a href="/register" className="font-medium text-white transition-colors hover:text-[#ff5962]">Create an account</a></>}
    >
      <LoginForm />
    </AuthShell>
  );
}
