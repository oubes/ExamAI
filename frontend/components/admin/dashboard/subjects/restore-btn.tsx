import { Button } from "@/components/ui/button";
import { useState } from "react";

import { educationService } from "@/services/subjects.service";

import { Loader2, RefreshCcw } from "lucide-react";

type RestoreBtnProps = {
	subjectId: string;
	onRestored: () => void;
};

export function RestoreBtn({ subjectId, onRestored }: RestoreBtnProps) {
	const [loading, setLoading] = useState(false);
	const handleRestore = async () => {
		setLoading(true);
		try {
			await educationService.restoreSubject(subjectId);
			onRestored();
		} catch (err) {
			console.error(err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<Button
			variant="ghost"
			onClick={() => handleRestore()}
			className="h-8 px-2 text-emerald-500/60 hover:text-emerald-400 hover:bg-emerald-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
            disabled={loading}
		>
			{loading ? (
				<>
					<Loader2 className="animate-spin h-3 w-3" />
					Loading...
				</>
			) : (
				<>
					<RefreshCcw className="h-3 w-3" /> Restore
				</>
			)}
		</Button>
	);
}
