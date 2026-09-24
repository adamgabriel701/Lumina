; ModuleID = 'matrix.ll'
source_filename = "matrix.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = local_unnamed_addr constant [1 x i8] zeroinitializer
@str_1 = local_unnamed_addr constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

declare ptr @GC_malloc(i64) local_unnamed_addr

declare void @GC_init() local_unnamed_addr

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #1

declare i64 @atoi(ptr) local_unnamed_addr

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  tail call void @GC_init()
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_then, label %if_end

if_then:                                          ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  br label %if_end

if_end:                                           ; preds = %main_entry, %if_then
  %n.0 = phi i64 [ %atoi_call, %if_then ], [ 200, %main_entry ]
  %mul = mul i64 %n.0, %n.0
  %alloc_size = shl i64 %mul, 3
  %alloc_call = tail call ptr @GC_malloc(i64 %alloc_size)
  %alloc_call.1 = tail call ptr @GC_malloc(i64 %alloc_size)
  %alloc_call.2 = tail call ptr @GC_malloc(i64 %alloc_size)
  %for_cond.113 = icmp sgt i64 %mul, 0
  br i1 %for_cond.113, label %for_body, label %for_cond.2.preheader

for_cond.2.preheader:                             ; preds = %for_body, %if_end
  %for_cond.321 = icmp sgt i64 %n.0, 0
  br i1 %for_cond.321, label %for_body.2.lr.ph, label %for_end.1

for_body:                                         ; preds = %if_end, %for_body
  %storemerge14 = phi i64 [ %for_next, %for_body ], [ 0, %if_end ]
  %mod = urem i64 %storemerge14, 10
  %.19 = getelementptr i64, ptr %alloc_call, i64 %storemerge14
  store i64 %mod, ptr %.19, align 8
  %mul.1 = shl nuw i64 %storemerge14, 1
  %mod.1 = srem i64 %mul.1, 10
  %.21 = getelementptr i64, ptr %alloc_call.1, i64 %storemerge14
  store i64 %mod.1, ptr %.21, align 8
  %.23 = getelementptr i64, ptr %alloc_call.2, i64 %storemerge14
  store i64 0, ptr %.23, align 8
  %for_next = add nuw nsw i64 %storemerge14, 1
  %exitcond.not = icmp eq i64 %for_next, %mul
  br i1 %exitcond.not, label %for_cond.2.preheader, label %for_body

for_body.2.lr.ph:                                 ; preds = %for_cond.2.preheader, %for_end.2
  %storemerge822 = phi i64 [ %for_next.3, %for_end.2 ], [ 0, %for_cond.2.preheader ]
  %mul.2 = mul i64 %storemerge822, %n.0
  %0 = getelementptr i64, ptr %alloc_call, i64 %mul.2
  %1 = getelementptr i64, ptr %alloc_call.2, i64 %mul.2
  br label %for_body.2

for_end.1:                                        ; preds = %for_end.2, %for_cond.2.preheader
  br i1 %for_cond.113, label %for_body.4.preheader, label %for_end.4

for_body.4.preheader:                             ; preds = %for_end.1
  %min.iters.check = icmp ult i64 %mul, 4
  br i1 %min.iters.check, label %for_body.4.preheader34, label %vector.ph

vector.ph:                                        ; preds = %for_body.4.preheader
  %n.vec = and i64 %mul, 9223372036854775804
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %index = phi i64 [ 0, %vector.ph ], [ %index.next, %vector.body ]
  %vec.phi = phi <2 x i64> [ zeroinitializer, %vector.ph ], [ %4, %vector.body ]
  %vec.phi32 = phi <2 x i64> [ zeroinitializer, %vector.ph ], [ %5, %vector.body ]
  %2 = getelementptr i64, ptr %alloc_call.2, i64 %index
  %3 = getelementptr i64, ptr %2, i64 2
  %wide.load = load <2 x i64>, ptr %2, align 8
  %wide.load33 = load <2 x i64>, ptr %3, align 8
  %4 = add <2 x i64> %wide.load, %vec.phi
  %5 = add <2 x i64> %wide.load33, %vec.phi32
  %index.next = add nuw i64 %index, 4
  %6 = icmp eq i64 %index.next, %n.vec
  br i1 %6, label %middle.block, label %vector.body, !llvm.loop !0

middle.block:                                     ; preds = %vector.body
  %bin.rdx = add <2 x i64> %5, %4
  %7 = tail call i64 @llvm.vector.reduce.add.v2i64(<2 x i64> %bin.rdx)
  %cmp.n = icmp eq i64 %mul, %n.vec
  br i1 %cmp.n, label %for_end.4, label %for_body.4.preheader34

for_body.4.preheader34:                           ; preds = %for_body.4.preheader, %middle.block
  %storemerge926.ph = phi i64 [ 0, %for_body.4.preheader ], [ %n.vec, %middle.block ]
  %add.42325.ph = phi i64 [ 0, %for_body.4.preheader ], [ %7, %middle.block ]
  br label %for_body.4

for_body.2:                                       ; preds = %for_body.2.lr.ph, %for_end.3
  %storemerge1120 = phi i64 [ 0, %for_body.2.lr.ph ], [ %for_next.2, %for_end.3 ]
  %invariant.gep = getelementptr i64, ptr %alloc_call.1, i64 %storemerge1120
  br label %for_body.3

for_end.2:                                        ; preds = %for_end.3
  %for_next.3 = add nuw nsw i64 %storemerge822, 1
  %exitcond30.not = icmp eq i64 %for_next.3, %n.0
  br i1 %exitcond30.not, label %for_end.1, label %for_body.2.lr.ph

for_body.3:                                       ; preds = %for_body.2, %for_body.3
  %storemerge1218 = phi i64 [ 0, %for_body.2 ], [ %for_next.1, %for_body.3 ]
  %add.21517 = phi i64 [ 0, %for_body.2 ], [ %add.2, %for_body.3 ]
  %.38 = getelementptr i64, ptr %0, i64 %storemerge1218
  %ptr_idx_load = load i64, ptr %.38, align 8
  %mul.3 = mul i64 %storemerge1218, %n.0
  %gep = getelementptr i64, ptr %invariant.gep, i64 %mul.3
  %ptr_idx_load.1 = load i64, ptr %gep, align 8
  %mul.4 = mul i64 %ptr_idx_load.1, %ptr_idx_load
  %add.2 = add i64 %mul.4, %add.21517
  %for_next.1 = add nuw nsw i64 %storemerge1218, 1
  %exitcond28.not = icmp eq i64 %for_next.1, %n.0
  br i1 %exitcond28.not, label %for_end.3, label %for_body.3

for_end.3:                                        ; preds = %for_body.3
  %.44 = getelementptr i64, ptr %1, i64 %storemerge1120
  store i64 %add.2, ptr %.44, align 8
  %for_next.2 = add nuw nsw i64 %storemerge1120, 1
  %exitcond29.not = icmp eq i64 %for_next.2, %n.0
  br i1 %exitcond29.not, label %for_end.2, label %for_body.2

for_body.4:                                       ; preds = %for_body.4.preheader34, %for_body.4
  %storemerge926 = phi i64 [ %for_next.4, %for_body.4 ], [ %storemerge926.ph, %for_body.4.preheader34 ]
  %add.42325 = phi i64 [ %add.4, %for_body.4 ], [ %add.42325.ph, %for_body.4.preheader34 ]
  %.56 = getelementptr i64, ptr %alloc_call.2, i64 %storemerge926
  %ptr_idx_load.2 = load i64, ptr %.56, align 8
  %add.4 = add i64 %ptr_idx_load.2, %add.42325
  %for_next.4 = add nuw nsw i64 %storemerge926, 1
  %exitcond31.not = icmp eq i64 %for_next.4, %mul
  br i1 %exitcond31.not, label %for_end.4, label %for_body.4, !llvm.loop !3

for_end.4:                                        ; preds = %for_body.4, %middle.block, %for_end.1
  %add.423.lcssa = phi i64 [ 0, %for_end.1 ], [ %7, %middle.block ], [ %add.4, %for_body.4 ]
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %add.423.lcssa)
  %putchar10 = tail call i32 @putchar(i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.vector.reduce.add.v2i64(<2 x i64>) #2

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #2 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!0 = distinct !{!0, !1, !2}
!1 = !{!"llvm.loop.isvectorized", i32 1}
!2 = !{!"llvm.loop.unroll.runtime.disable"}
!3 = distinct !{!3, !2, !1}
