import BackendStatus from "@/components/BackendStatus";
import Feed from "@/components/Feed";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-16">
      <header className="flex flex-col gap-4">
        <p className="text-sm font-medium uppercase tracking-widest text-sky-400">
          Curadoria inteligente de conhecimento
        </p>
        <h1 className="text-4xl font-semibold tracking-tight text-zinc-50">
          Conteúdo que vale o seu tempo.
        </h1>
        <p className="max-w-xl text-lg leading-8 text-zinc-400">
          Uma plataforma que encontra, analisa e classifica conteúdos pela profundidade e
          qualidade, e não pela popularidade.
        </p>
        <div>
          <BackendStatus />
        </div>
      </header>

      <Feed />
    </main>
  );
}
