import { Switch } from "@/components/ui/switch";
import { Loader2 } from "lucide-react";
import { useState } from "react";

import { educationService } from "@/services/subjects.service";

type ActiveTogglerProps = {
	subjectId: string;
	active: boolean;
	onToggle: (newStatus: boolean) => void;
};

export function ActiveToggler({
	subjectId,
	active,
	onToggle,
}: ActiveTogglerProps) {
	const [loading, setLoading] = useState(false);

	const handleToggleActive = async (newStatus: boolean) => {
		setLoading(true);
		try {
			const updated = await educationService.updateSubject(subjectId, {
				is_active: newStatus,
			});
			onToggle(updated.is_active);
		} catch (err) {
			console.error(err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="flex items-center gap-2 mr-2">
			{loading ? (
				<Loader2 className="animate-spin w-4 h-4" />
			) : (
				<span
					className={`text-[9px] font-bold uppercase transition-colors ${active ? "text-blue-500" : "text-zinc-600"}`}
				>
					{active ? "Active" : "Off"}
				</span>
			)}
			<Switch
				checked={active}
				onCheckedChange={() => handleToggleActive(!active)}
				className="data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-zinc-800 border-zinc-700 scale-75 cursor-pointer"
				disabled={loading}
			/>
		</div>
	);
}
