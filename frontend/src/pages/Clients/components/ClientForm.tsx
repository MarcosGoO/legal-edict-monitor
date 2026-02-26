import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import AliasInput from '../../../components/ui/AliasInput'
import type { ClientCreate, ClientResponse, DocumentType } from '../../../types/api'

// ── Zod schema ──────────────────────────────────────────────────────────────

const schema = z.object({
  full_name: z
    .string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .max(500, 'El nombre es demasiado largo'),
  document_type: z
    .enum(['CC', 'CE', 'NIT', 'PP', 'TI'])
    .nullable()
    .optional(),
  document_number: z
    .string()
    .max(20, 'Máximo 20 caracteres')
    .regex(/^\d*$/, 'Solo se permiten dígitos')
    .nullable()
    .optional(),
  nit: z
    .string()
    .max(20, 'Máximo 20 caracteres')
    .nullable()
    .optional(),
  aliases: z.array(z.string()),
  notes: z.string().nullable().optional(),
  is_active: z.boolean().optional(),
})

type FormValues = z.infer<typeof schema>

// ── Field wrapper ────────────────────────────────────────────────────────────

function Field({
  label,
  hint,
  error,
  required,
  children,
}: {
  label: string
  hint?: string
  error?: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
        {hint && <span className="ml-1.5 text-xs text-slate-400 font-normal">{hint}</span>}
      </label>
      {children}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}

const inputCls =
  'w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent'

// ── Component ────────────────────────────────────────────────────────────────

interface ClientFormProps {
  defaultValues?: ClientResponse
  onSubmit: (data: ClientCreate) => Promise<void>
  isLoading: boolean
}

const DOCUMENT_TYPES: { value: DocumentType; label: string }[] = [
  { value: 'CC', label: 'Cédula de Ciudadanía (CC)' },
  { value: 'CE', label: 'Cédula de Extranjería (CE)' },
  { value: 'NIT', label: 'NIT' },
  { value: 'PP', label: 'Pasaporte (PP)' },
  { value: 'TI', label: 'Tarjeta de Identidad (TI)' },
]

export default function ClientForm({ defaultValues, onSubmit, isLoading }: ClientFormProps) {
  const navigate = useNavigate()
  const isEdit = !!defaultValues

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: defaultValues?.full_name ?? '',
      document_type: defaultValues?.document_type ?? null,
      document_number: defaultValues?.document_number ?? '',
      nit: defaultValues?.nit ?? '',
      aliases: defaultValues?.aliases ?? [],
      notes: '',
      is_active: defaultValues?.is_active ?? true,
    },
  })

  const submit = handleSubmit(async (values) => {
    await onSubmit({
      full_name: values.full_name,
      document_type: (values.document_type as DocumentType) ?? null,
      document_number: values.document_number || null,
      nit: values.nit || null,
      aliases: values.aliases,
      notes: values.notes || null,
    })
  })

  return (
    <form onSubmit={submit} className="space-y-5 max-w-xl">
      <Field label="Nombre completo" required error={errors.full_name?.message}>
        <input
          {...register('full_name')}
          placeholder="JOSÉ MARÍA RODRÍGUEZ GARCÍA"
          className={inputCls}
          style={{ textTransform: 'uppercase' }}
        />
      </Field>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Tipo de documento" error={errors.document_type?.message}>
          <select {...register('document_type')} className={inputCls}>
            <option value="">Sin documento</option>
            {DOCUMENT_TYPES.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </Field>

        <Field
          label="Número de documento"
          hint="Solo dígitos"
          error={errors.document_number?.message}
        >
          <input
            {...register('document_number')}
            placeholder="12345678"
            className={`${inputCls} font-mono`}
          />
        </Field>
      </div>

      <Field
        label="NIT"
        hint="Formato: 900123456-7"
        error={errors.nit?.message}
      >
        <input
          {...register('nit')}
          placeholder="900123456-7"
          className={`${inputCls} font-mono`}
        />
      </Field>

      <Field
        label="Aliases"
        hint="Nombres alternativos para la búsqueda — presiona Enter para agregar"
        error={errors.aliases?.message as string}
      >
        <Controller
          name="aliases"
          control={control}
          render={({ field }) => (
            <AliasInput value={field.value} onChange={field.onChange} />
          )}
        />
      </Field>

      <Field label="Notas" error={errors.notes?.message}>
        <textarea
          {...register('notes')}
          rows={3}
          placeholder="Observaciones internas sobre el cliente…"
          className={inputCls}
        />
      </Field>

      {isEdit && (
        <Field label="Estado">
          <label className="flex items-center gap-2 cursor-pointer">
            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <input
                  type="checkbox"
                  checked={field.value}
                  onChange={field.onChange}
                  className="w-4 h-4 rounded accent-brand-500"
                />
              )}
            />
            <span className="text-sm text-slate-700">Cliente activo</span>
          </label>
        </Field>
      )}

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="px-5 py-2 bg-brand-500 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-60"
        >
          {isLoading ? 'Guardando…' : isEdit ? 'Guardar cambios' : 'Crear cliente'}
        </button>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="px-5 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
