import * as Dialog from "@radix-ui/react-dialog";
import { MapPin, Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { MapContainer, Marker, TileLayer, useMapEvents } from "react-leaflet";
import { Button, Input } from "@/components/ui";
import { nominatimProvider, type GeoLocation } from "@/lib/geocoding";

function ClickMarker({
  value,
  onChange,
}: {
  value?: GeoLocation;
  onChange: (lat: number, lng: number) => void;
}) {
  useMapEvents({ click: ({ latlng }) => onChange(latlng.lat, latlng.lng) });
  return value ? (
    <Marker
      position={[value.latitude, value.longitude]}
      draggable
      eventHandlers={{
        dragend: (event) => {
          const point = event.target.getLatLng();
          onChange(point.lat, point.lng);
        },
      }}
    />
  ) : null;
}

export function LocationPicker({
  value,
  onConfirm,
}: {
  value?: GeoLocation;
  onConfirm: (value: GeoLocation) => void;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<GeoLocation | undefined>(value);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GeoLocation[]>([]);
  const [message, setMessage] = useState(
    "Haz clic en el mapa o busca una dirección.",
  );
  const request = useRef<AbortController | null>(null);
  useEffect(() => {
    if (!open || query.trim().length < 3) return;
    const timer = window.setTimeout(async () => {
      request.current?.abort();
      request.current = new AbortController();
      try {
        setResults(
          await nominatimProvider.search(query, request.current.signal),
        );
        setMessage("Selecciona un resultado o marca el punto exacto.");
      } catch (error) {
        if ((error as Error).name !== "AbortError")
          setMessage((error as Error).message);
      }
    }, 450);
    return () => window.clearTimeout(timer);
  }, [open, query]);
  async function locate(latitude: number, longitude: number) {
    request.current?.abort();
    request.current = new AbortController();
    const fallback = {
      latitude,
      longitude,
      address: "",
      neighborhood: "",
      city: "",
      department: "",
    };
    setDraft(fallback);
    setMessage("Detectando dirección…");
    try {
      setDraft(
        await nominatimProvider.reverse(
          latitude,
          longitude,
          request.current.signal,
        ),
      );
      setMessage("Ubicación detectada. Puedes ajustar sus datos.");
    } catch (error) {
      setMessage((error as Error).message);
    }
  }
  return (
    <>
      <Button
        type="button"
        variant="secondary"
        className="w-full justify-center"
        onClick={() => {
          setDraft(value);
          setOpen(true);
        }}
      >
        <MapPin size={17} />
        {value ? "Cambiar ubicación en mapa" : "Seleccionar ubicación en mapa"}
      </Button>
      <Dialog.Root open={open} onOpenChange={setOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm" />
          <Dialog.Content className="fixed inset-2 z-50 flex flex-col overflow-hidden rounded-2xl bg-white shadow-2xl outline-none sm:inset-6 lg:inset-10">
            <header className="flex items-center justify-between border-b px-4 py-3 sm:px-6">
              <div>
                <Dialog.Title className="font-bold text-slate-950">
                  Seleccionar ubicación
                </Dialog.Title>
                <Dialog.Description className="text-xs text-slate-500">
                  Busca o coloca el pin en cualquier ciudad de Bolivia.
                </Dialog.Description>
              </div>
              <Dialog.Close
                className="rounded-lg p-2 hover:bg-slate-100"
                aria-label="Cerrar"
              >
                <X size={20} />
              </Dialog.Close>
            </header>
            <div className="relative border-b p-3 sm:px-6">
              <Search
                className="absolute left-6 top-6 text-slate-400 sm:left-9"
                size={18}
              />
              <Input
                aria-label="Buscar calle, zona o ciudad"
                className="pl-10"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Buscar calle, zona o ciudad…"
              />
              {results.length > 0 && (
                <div className="absolute left-3 right-3 top-14 z-[1001] max-h-52 overflow-auto rounded-xl border bg-white p-1 shadow-xl sm:left-6 sm:right-6">
                  {results.map((item) => (
                    <button
                      type="button"
                      key={`${item.latitude}-${item.longitude}`}
                      className="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-emerald-50"
                      onClick={() => {
                        setDraft(item);
                        setResults([]);
                        setQuery("");
                      }}
                    >
                      {item.address}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="min-h-56 flex-1">
              <MapContainer
                key={draft ? `${draft.latitude}-${draft.longitude}` : "default"}
                center={
                  draft ? [draft.latitude, draft.longitude] : [-16.7, -64.7]
                }
                zoom={draft ? 15 : 5}
                className="h-full w-full"
              >
                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <ClickMarker
                  value={draft}
                  onChange={(lat, lng) => void locate(lat, lng)}
                />
              </MapContainer>
            </div>
            <footer className="grid gap-3 border-t p-4 sm:grid-cols-[1fr_auto] sm:px-6">
              <div>
                <p className="text-xs text-slate-500">{message}</p>
                {draft && (
                  <p className="mt-1 line-clamp-2 text-sm font-semibold text-slate-800">
                    {draft.address ||
                      "Punto seleccionado; completa la dirección después."}
                  </p>
                )}
              </div>
              <Button
                type="button"
                disabled={!draft}
                onClick={() => {
                  if (draft) {
                    onConfirm(draft);
                    setOpen(false);
                  }
                }}
              >
                Confirmar ubicación
              </Button>
            </footer>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </>
  );
}
