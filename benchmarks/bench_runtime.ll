; ModuleID = 'bench_runtime.ll'
source_filename = "bench_runtime.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = constant [11 x i8] c"Resultado:\00"
@str_1 = constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"
@str_5 = constant [16 x i8] c"Lumina Runtime:\00"
@str_6 = constant [3 x i8] c"%s\00"
@str_7 = local_unnamed_addr constant [2 x i8] c" \00"
@str_8 = constant [3 x i8] c"%f\00"
@str_9 = constant [9 x i8] c"segundos\00"
@str_10 = local_unnamed_addr constant [2 x i8] c" \00"
@str_11 = constant [3 x i8] c"%s\00"
@str_12 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

declare void @GC_init() local_unnamed_addr

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #1

declare i64 @atoi(ptr) local_unnamed_addr

declare i64 @clock() local_unnamed_addr

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define i64 @somar(i64 %.1, i64 %.2) local_unnamed_addr #2 {
somar_entry:
  %add = add i64 %.2, %.1
  ret i64 %add
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define i64 @dividir(i64 %.1, i64 %.2) local_unnamed_addr #2 {
dividir_entry:
  %icmp = icmp eq i64 %.2, 0
  br i1 %icmp, label %common.ret, label %if_end

common.ret:                                       ; preds = %dividir_entry, %if_end
  %common.ret.op = phi i64 [ %div, %if_end ], [ 0, %dividir_entry ]
  ret i64 %common.ret.op

if_end:                                           ; preds = %dividir_entry
  %div = sdiv i64 %.1, %.2
  br label %common.ret
}

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  tail call void @GC_init()
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_end, label %if_end.thread

if_end.thread:                                    ; preds = %main_entry
  %clock_call10 = tail call i64 @clock()
  br label %for_body.preheader

if_end:                                           ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  %clock_call = tail call i64 @clock()
  %for_cond.16 = icmp sgt i64 %atoi_call, 0
  br i1 %for_cond.16, label %for_body.preheader, label %for_end

for_body.preheader:                               ; preds = %if_end.thread, %if_end
  %clock_call14 = phi i64 [ %clock_call10, %if_end.thread ], [ %clock_call, %if_end ]
  %limit.012 = phi i64 [ 10000000, %if_end.thread ], [ %atoi_call, %if_end ]
  %0 = add nsw i64 %limit.012, -1
  %1 = zext nneg i64 %0 to i65
  %2 = add nsw i64 %limit.012, -2
  %3 = zext i64 %2 to i65
  %4 = mul i65 %1, %3
  %5 = lshr i65 %4, 1
  %6 = trunc i65 %5 to i64
  %7 = add i64 %limit.012, %6
  %8 = add i64 %7, -1
  br label %for_end

for_end:                                          ; preds = %for_body.preheader, %if_end
  %clock_call13 = phi i64 [ %clock_call, %if_end ], [ %clock_call14, %for_body.preheader ]
  %add5.lcssa = phi i64 [ 0, %if_end ], [ %8, %for_body.preheader ]
  %print_call = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_1, ptr nonnull @str_0)
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %add5.lcssa)
  %putchar1 = tail call i32 @putchar(i32 10)
  %clock_call.1 = tail call i64 @clock()
  %sub = sub i64 %clock_call.1, %clock_call13
  %int_to_float = sitofp i64 %sub to double
  %float_to_int_store = fptosi double %int_to_float to i64
  %int_to_float.1 = sitofp i64 %float_to_int_store to double
  %fdiv = fdiv double %int_to_float.1, 1.000000e+06
  %print_call.2 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_6, ptr nonnull @str_5)
  %putchar2 = tail call i32 @putchar(i32 32)
  %print_call.3 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_8, double %fdiv)
  %putchar3 = tail call i32 @putchar(i32 32)
  %print_call.4 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_11, ptr nonnull @str_9)
  %putchar4 = tail call i32 @putchar(i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #2 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }
