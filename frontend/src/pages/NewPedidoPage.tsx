import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, LoaderCircle } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";
import { LocationPicker } from "@/components/LocationPicker";
import {
  Button,
  Card,
  Field,
  Input,
  PageHeader,
  Select,
  Textarea,
} from "@/components/ui";
import { api, errorMessage } from "@/lib/api";
import type { GeoLocation } from "@/lib/geocoding";

const schema = z.object({
  nombre: z.string().trim().min(1, "El nombre es obligatorio"),
  telefono: z.string().trim(),
  email: z.string().trim().email("Ingresa un correo válido").or(z.literal("")),
  direccion: z.string().trim().min(1, "Selecciona o escribe una dirección"),
  zona: z.string().trim().min(1, "La zona es obligatoria"),
  ciudad: z.string().trim(),
  departamento: z.string().trim(),
  codigo: z.string().trim().min(1, "El código es obligatorio"),
  fecha_limite: z
    .string()
    .min(1, "La fecha límite es obligatoria")
    .refine(
      (value) => new Date(value).getTime() > Date.now(),
      "Selecciona una fecha y hora futuras.",
    ),
  peso_kg: z
    .string()
    .refine((value) => Number(value) > 0, "El peso debe ser mayor a cero"),
  urgencia: z.enum(["1", "2", "3", "4", "5"]),
});
type Values = z.infer<typeof schema>;
const minimumDeliveryDate = new Date(Date.now() + 60_000)
  .toISOString()
  .slice(0, 16);
const steps = ["Cliente", "Destino", "Carga y entrega", "Confirmación"];

export function NewPedidoPage() {
  const navigate = useNavigate();
  const client = useQueryClient();
  const [step, setStep] = useState(0);
  const [location, setLocation] = useState<GeoLocation>();
  const [clientSearch, setClientSearch] = useState("");
  const [selectedClient, setSelectedClient] = useState("");
  const [newClient, setNewClient] = useState(false);
  const clients = useQuery({ queryKey: ["clientes", clientSearch], queryFn: () => api.clientes(clientSearch || undefined) });
  const {
    register,
    handleSubmit,
    setValue,
    trigger,
    getValues,
    formState: { errors },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    mode: "onBlur",
    defaultValues: {
      nombre: "",
      telefono: "",
      email: "",
      direccion: "",
      zona: "",
      ciudad: "",
      departamento: "",
      codigo: "",
      fecha_limite: "",
      peso_kg: "",
      urgencia: "3",
    },
  });
  const create = useMutation({
    mutationFn: (v: Values) =>
      api.crearPedido({
        ...(selectedClient && !newClient ? { id_cliente: Number(selectedClient) } : { cliente: {
          nombre: v.nombre,
          ...(v.telefono && { telefono: v.telefono }),
          ...(v.email && { email: v.email }),
        } }),
        ubicacion: {
          direccion: v.direccion,
          zona: v.zona,
          ciudad: v.ciudad,
          departamento: v.departamento,
          ...(location && {
            latitud: location.latitude,
            longitud: location.longitude,
          }),
        },
        pedido: {
          codigo: v.codigo.toUpperCase(),
          peso_kg: Number(v.peso_kg),
          urgencia: Number(v.urgencia),
          fecha_limite: new Date(v.fecha_limite).toISOString(),
        },
      }),
    onSuccess: async (pedido) => {
      toast.success("Pedido guardado correctamente");
      await Promise.all([
        client.invalidateQueries({ queryKey: ["pedidos"] }),
        client.invalidateQueries({ queryKey: ["resumen"] }),
      ]);
      navigate(`/pedidos/${pedido.id_pedido}`);
    },
    onError: (error) => toast.error(errorMessage(error)),
  });
  async function next() {
    const fields: (keyof Values)[][] = [
      ["nombre", "email"],
      ["direccion", "zona"],
      ["codigo", "fecha_limite", "peso_kg", "urgencia"],
      [],
    ];
    if (await trigger(fields[step])) setStep((value) => Math.min(3, value + 1));
  }
  const values = getValues();
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <Link
          to="/pedidos"
          className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={16} />
          Volver a pedidos
        </Link>
        <PageHeader
          eyebrow="Flujo guiado"
          title="Registrar pedido"
          description="Solo pedimos la información necesaria para preparar la entrega."
        />
      </div>
      <ol className="grid grid-cols-4 gap-2" aria-label="Progreso">
        {steps.map((label, index) => (
          <li
            key={label}
            className={`rounded-xl border p-3 text-xs font-semibold ${index === step ? "border-emerald-500 bg-emerald-50 text-emerald-800" : index < step ? "border-emerald-200 text-emerald-700" : "border-slate-200 text-slate-400"}`}
          >
            <span className="mr-2 inline-grid h-5 w-5 place-items-center rounded-full bg-current/10">
              {index < step ? <Check size={13} /> : index + 1}
            </span>
            <span className="hidden sm:inline">{label}</span>
          </li>
        ))}
      </ol>
      <form onSubmit={handleSubmit((data) => create.mutate(data))} noValidate>
        <Card className="p-5 sm:p-7">
          {step === 0 && (
            <section>
              <h2 className="text-xl font-bold">¿Quién recibe?</h2>
              <p className="mb-6 mt-1 text-sm text-slate-500">Busca un cliente existente o registra uno nuevo.</p>
              {!newClient && <div className="space-y-4">
                <Field label="Buscar cliente"><Input value={clientSearch} onChange={(event) => setClientSearch(event.target.value)} placeholder="Nombre, teléfono o email…" /></Field>
                <Field label="Cliente" required><Select aria-label="Seleccionar cliente" value={selectedClient} onChange={(event) => {
                  setSelectedClient(event.target.value);
                  const selected = clients.data?.find((item) => item.id_cliente === Number(event.target.value));
                  if (selected) { setValue("nombre", selected.nombre); setValue("telefono", selected.telefono ?? ""); setValue("email", selected.email ?? ""); }
                }}><option value="">Selecciona un cliente…</option>{clients.data?.map((item) => <option key={item.id_cliente} value={item.id_cliente}>{item.nombre} · {item.telefono || "sin teléfono"}{item.email ? ` · ${item.email}` : ""}</option>)}</Select></Field>
              </div>}
              <button type="button" className="my-5 text-sm font-semibold text-emerald-700 hover:text-emerald-600" onClick={() => { setNewClient((value) => !value); setSelectedClient(""); }}>{newClient ? "← Seleccionar cliente existente" : "+ Nuevo cliente"}</button>
              {newClient && <div className="grid gap-4 sm:grid-cols-2">
                <Field
                  label="Nombre del cliente"
                  error={errors.nombre?.message}
                  required
                >
                  <Input {...register("nombre")} autoComplete="name" />
                </Field>
                <Field label="Teléfono">
                  <Input {...register("telefono")} type="tel" />
                </Field>
                <Field label="Correo electrónico" error={errors.email?.message}>
                  <Input {...register("email")} type="email" />
                </Field>
              </div>}
            </section>
          )}
          {step === 1 && (
            <section>
              <h2 className="text-xl font-bold">¿Dónde entregamos?</h2>
              <p className="mb-6 mt-1 text-sm text-slate-500">
                Busca la dirección o marca el punto exacto en el mapa.
              </p>
              <div className="space-y-4">
                <LocationPicker
                  value={location}
                  onConfirm={(place) => {
                    setLocation(place);
                    setValue("direccion", place.address, {
                      shouldValidate: true,
                    });
                    setValue("zona", place.neighborhood || "Sin especificar", {
                      shouldValidate: true,
                    });
                    setValue("ciudad", place.city);
                    setValue("departamento", place.department);
                  }}
                />
                <Field
                  label="Dirección"
                  error={errors.direccion?.message}
                  required
                >
                  <Textarea {...register("direccion")} />
                </Field>
                <div className="grid gap-4 sm:grid-cols-3">
                  <Field
                    label="Zona o barrio"
                    error={errors.zona?.message}
                    required
                  >
                    <Input {...register("zona")} />
                  </Field>
                  <Field label="Ciudad">
                    <Input {...register("ciudad")} />
                  </Field>
                  <Field label="Departamento">
                    <Input {...register("departamento")} />
                  </Field>
                </div>
              </div>
            </section>
          )}
          {step === 2 && (
            <section>
              <h2 className="text-xl font-bold">Carga y entrega</h2>
              <p className="mb-6 mt-1 text-sm text-slate-500">
                Condiciones necesarias para planificar recursos.
              </p>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field
                  label="Código del pedido"
                  error={errors.codigo?.message}
                  required
                >
                  <Input
                    {...register("codigo")}
                    className="uppercase"
                    placeholder="ORD-2026-001"
                  />
                </Field>
                <Field
                  label="Fecha y hora límite"
                  error={errors.fecha_limite?.message}
                  required
                >
                  <Input
                    {...register("fecha_limite")}
                    type="datetime-local"
                    min={minimumDeliveryDate}
                  />
                </Field>
                <Field
                  label="Peso de la carga"
                  hint="Ingresa el peso total en kilogramos."
                  error={errors.peso_kg?.message}
                  required
                >
                  <div className="relative">
                    <Input
                      {...register("peso_kg")}
                      type="number"
                      min="0.01"
                      step="0.01"
                      className="pr-12"
                    />
                    <span className="absolute right-3 top-3 text-sm text-slate-500">
                      kg
                    </span>
                  </div>
                </Field>
                <Field
                  label="Urgencia"
                  error={errors.urgencia?.message}
                  required
                >
                  <Select {...register("urgencia")}>
                    <option value="1">Baja</option>
                    <option value="2">Normal</option>
                    <option value="3">Media</option>
                    <option value="4">Alta</option>
                    <option value="5">Crítica</option>
                  </Select>
                </Field>
              </div>
            </section>
          )}
          {step === 3 && (
            <section>
              <h2 className="text-xl font-bold">Confirma el pedido</h2>
              <p className="mb-6 mt-1 text-sm text-slate-500">
                Revisa antes de registrarlo.
              </p>
              <dl className="grid gap-4 rounded-xl bg-slate-50 p-5 sm:grid-cols-2">
                <div>
                  <dt className="text-xs text-slate-500">Cliente</dt>
                  <dd className="font-semibold">{values.nombre}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-500">Pedido</dt>
                  <dd className="font-semibold">
                    {values.codigo.toUpperCase()}
                  </dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-xs text-slate-500">Destino</dt>
                  <dd className="font-semibold">{values.direccion}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-500">Carga</dt>
                  <dd className="font-semibold">{values.peso_kg} kg</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-500">Fecha límite</dt>
                  <dd className="font-semibold">
                    {new Date(values.fecha_limite).toLocaleString("es-BO")}
                  </dd>
                </div>
              </dl>
            </section>
          )}
        </Card>
        <div className="mt-5 flex justify-between">
          <Button
            type="button"
            variant="secondary"
            disabled={step === 0}
            onClick={() => setStep((value) => value - 1)}
          >
            <ArrowLeft size={17} />
            Anterior
          </Button>
          {step < 3 ? (
            <Button type="button" onClick={() => void next()}>
              Continuar
              <ArrowRight size={17} />
            </Button>
          ) : (
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? (
                <LoaderCircle className="animate-spin" size={17} />
              ) : (
                <Check size={17} />
              )}
              Registrar pedido
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
