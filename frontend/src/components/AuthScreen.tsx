"use client";

import { FormEvent, useState } from "react";
import { login, register, type AuthUser } from "@/lib/auth";
import styles from "./AuthScreen.module.css";

export function AuthScreen({
  onAuthenticated,
}: {
  onAuthenticated: (user: AuthUser) => void;
}) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const result =
        mode === "login"
          ? await login(String(form.get("email")), String(form.get("password")))
          : await register(
              String(form.get("display_name")),
              String(form.get("email")),
              String(form.get("password")),
            );
      onAuthenticated(result.user);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Não foi possível autenticar.",
      );
    } finally {
      setWorking(false);
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.presentation}>
        <div className={styles.brand}>
          <span aria-hidden="true">◇</span>
          Nexus d20
        </div>
        <div className={styles.copy}>
          <span>Seu grimório de campanha</span>
          <h1>Entre nas sombras.<br />Conduza sua história.</h1>
          <p>
            Fichas, evolução, inventário e ferramentas do mestre em um único
            ambiente seguro para D&amp;D 5e de 2014.
          </p>
        </div>
        <small>Versão web responsiva · Nexus d20 1.0.1</small>
      </section>

      <section className={styles.access} aria-labelledby="access-title">
        <div className={styles.mobileBrand}>◇ Nexus d20</div>
        <div className={styles.tabs} role="tablist" aria-label="Acesso à conta">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "login"}
            onClick={() => {
              setMode("login");
              setError("");
            }}
          >
            Entrar
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "register"}
            onClick={() => {
              setMode("register");
              setError("");
            }}
          >
            Criar conta
          </button>
        </div>

        <div className={styles.formHeading}>
          <span>{mode === "login" ? "Bem-vindo de volta" : "Novo aventureiro"}</span>
          <h2 id="access-title">
            {mode === "login" ? "Acesse sua campanha" : "Crie seu acesso"}
          </h2>
          <p>
            {mode === "login"
              ? "Use o e-mail cadastrado para continuar."
              : "Sua primeira campanha será criada depois do cadastro."}
          </p>
        </div>

        <form onSubmit={submit}>
          {mode === "register" && (
            <label>
              Nome de exibição
              <input
                name="display_name"
                autoComplete="name"
                minLength={2}
                maxLength={120}
                required
                placeholder="Como devemos chamar você?"
              />
            </label>
          )}
          <label>
            E-mail
            <input
              name="email"
              type="email"
              autoComplete="email"
              required
              placeholder="voce@exemplo.com"
            />
          </label>
          <label>
            Senha
            <input
              name="password"
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              minLength={mode === "register" ? 12 : 1}
              maxLength={128}
              required
              placeholder={mode === "register" ? "No mínimo 12 caracteres" : "Sua senha"}
            />
          </label>
          {error && <p className={styles.error} role="alert">{error}</p>}
          <button className={styles.submit} type="submit" disabled={working}>
            {working
              ? "Aguarde…"
              : mode === "login"
                ? "Entrar no Nexus"
                : "Criar conta"}
          </button>
        </form>
        <p className={styles.terms}>
          Ao continuar, você concorda com os termos de uso e a política de
          privacidade do ambiente.
        </p>
      </section>
    </main>
  );
}
